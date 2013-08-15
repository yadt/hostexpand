#!/usr/bin/env python

import unittest
import dns.resolver

from mockito import unstub, when, verify, any as any_value

from tempfile import NamedTemporaryFile

import hostexpand.HostExpander as hostexpander
from hostexpand.HostExpander import HostExpander


class HostExpanderTestBase(unittest.TestCase):

    def expand_and_assert(self, expander_expression, *expected_host_names):
        actual = self.expander.expand(expander_expression)
        self.assertEquals(list(expected_host_names), actual)

    def tearDown(self):
        unstub()


class ShortnameHostExpanderTest(HostExpanderTestBase):

    def setUp(self):
        self.expander = HostExpander()

    def test_should_raise_value_error_when_expanding_none(self):
        self.assertRaises(ValueError, self.expander.expand, None)

    def test_should_return_empty_set_when_expanding_empty_string(self):
        self.expand_and_assert("")

    def test_should_expand_constant_expression(self):
        self.expand_and_assert("spam01", "spam01")

    def test_should_expand_hostname_alternatives(self):
        self.expand_and_assert("{spam|eggs}01", "eggs01", "spam01")

    def test_should_expand_host_number_range_to_single_host(self):
        when(dns.resolver).query("spam01").thenReturn(None)
        self.expand_and_assert("spam[1:2]", "spam01")
        verify(dns.resolver).query("spam01")

    def test_should_expand_host_number_range_to_single_host_when_second_host_cannot_be_resolved(self):
        when(dns.resolver).query("spam01").thenReturn(None)
        when(dns.resolver).query("spam02").thenRaise(
            dns.resolver.NXDOMAIN("Caboom"))

        self.expand_and_assert("spam[1:3]", "spam01")

        verify(dns.resolver).query("spam01")
        verify(dns.resolver).query("spam02")

    def test_should_expand_host_number_range_with_open_starting_range(self):
        when(dns.resolver).query(any_value()).thenReturn(None)

        self.expand_and_assert("spam[..2]", "spam01", "spam02")

        verify(dns.resolver, 0).query("spam00")
        verify(dns.resolver).query("spam01")
        verify(dns.resolver).query("spam02")

    def test_should_expand_host_number_range_with_just_one_single_number_in_it(self):
        when(dns.resolver).query('spam02').thenReturn(None)
        self.expand_and_assert("spam[2]", "spam02")
        verify(dns.resolver).query("spam02")

    def test_should_expand_host_number_range_with_open_ending_range(self):
        when(dns.resolver).query("spam02").thenReturn(None)
        when(dns.resolver).query("spam03").thenReturn(None)
        when(dns.resolver).query("spam04").thenRaise(
            dns.resolver.NXDOMAIN("Caboom"))

        self.expand_and_assert("spam[2..]", "spam02", "spam03")

        verify(dns.resolver).query("spam02")
        verify(dns.resolver).query("spam03")
        verify(dns.resolver).query("spam04")

    def test_should_expand_host_number_range_with_multiple_exclusion_ranges(self):
        when(dns.resolver).query(any_value()).thenReturn(None)

        self.expand_and_assert(
            "spam[1..7] -spam[2..3] !spam[5..6]", "spam01", "spam04", "spam07")

        verify(dns.resolver).query("spam01")
        verify(dns.resolver, 2).query("spam02")
        verify(dns.resolver, 2).query("spam03")
        verify(dns.resolver).query("spam04")
        verify(dns.resolver, 2).query("spam05")
        verify(dns.resolver, 2).query("spam06")
        verify(dns.resolver).query("spam07")


class FqdnHostExpanderTest(HostExpanderTestBase):

    def setUp(self):
        self.expander = HostExpander(outputformat=HostExpander.FQDN)

    def test_should_expand_short_name_to_single_host_with_fqdn(self):
        when(hostexpander.socket).getfqdn(
            "spam01").thenReturn("spam01.long.domain.name")
        self.expand_and_assert("spam01", "spam01.long.domain.name")
        verify(hostexpander.socket).getfqdn("spam01")


class IpHostExpanderTest(HostExpanderTestBase):

    def setUp(self):
        self.expander = HostExpander(outputformat=HostExpander.IP)

    def test_should_expand_single_host_name_to_ip_address(self):
        when(hostexpander.socket).gethostbyname(
            "spam01").thenReturn("192.168.111.112")
        self.expand_and_assert("spam01", "192.168.111.112")
        verify(hostexpander.socket).gethostbyname("spam01")


class FileHostExpanderTest(HostExpanderTestBase):

    def setUp(self):
        self.expander = HostExpander(outputformat=HostExpander.IP)
        self.datafile = NamedTemporaryFile()
                                           # give fully qualified path name
                                           # which triggers file expansion
        self.datafile.write("spam01.domain\nspam02.domain\n")
        self.datafile.flush()

    def tearDown(self):
        self.datafile.close()

    def test_should_ignore_inline_comments_when_expanding_file(self):
        when(hostexpander.socket).gethostbyname(
            "spam01.domain").thenReturn("192.168.111.112")
        when(hostexpander.socket).gethostbyname(
            "spam02.domain").thenReturn("192.168.111.113")
        when(hostexpander.socket).gethostbyname(
            "spam03.domain").thenReturn("192.168.111.254")
        self.datafile.write("spam03.domain # ignore me\n")
        self.datafile.flush()

        self.expand_and_assert(
            self.datafile.name, "192.168.111.112",
                                "192.168.111.113",
                                "192.168.111.254")

    def test_should_expand_single_file_with_two_names_to_ip_address(self):
        when(hostexpander.socket).gethostbyname(
            "spam01.domain").thenReturn("192.168.111.112")
        when(hostexpander.socket).gethostbyname(
            "spam02.domain").thenReturn("192.168.111.113")

        self.expand_and_assert(
            self.datafile.name, "192.168.111.112", "192.168.111.113")
        verify(hostexpander.socket).gethostbyname("spam01.domain")
        verify(hostexpander.socket).gethostbyname("spam02.domain")
