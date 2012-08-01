#!/usr/bin/env python
import sys
import socket
import dns.resolver

class HostExpander(object):
    IP = 'ip'
    FQDN = 'fqdn'
    SHORTNAME = 'shortname'

    def __init__(self, nrformat=None, outputformat=None, start_nr=1, substract_prefix=None):
        self.nrformat = nrformat
        if not self.nrformat:
            self.nrformat = '%02i'
        self.outputformat = outputformat
        if not self.outputformat:
            self.outputformat = HostExpander.SHORTNAME
        self.start_nr = start_nr
        self.substract_prefix = substract_prefix if substract_prefix else set(['-', '!'])

    def _expand_nr(self, name, start, end):
        if not start:
            start = self.start_nr
        if not end:
            end = sys.maxint
        for i in xrange(int(start), int(end)):
            nr = self.nrformat % i
            yield name % nr

    def _get_hostname(self, name):
        if self.outputformat == HostExpander.IP:
            return socket.gethostbyname(name)
        elif self.outputformat == HostExpander.SHORTNAME:
            return socket.getfqdn(name).split('.', 1)[0]
        return socket.getfqdn(name)

    def _get_hostnames(self, pattern, start=None, end=None):
        for hostname in self._expand_nr(pattern, start, end):
            try:
                dns.resolver.query(hostname)
                yield self._get_hostname(hostname)
            except:
                raise StopIteration()

    def _expand_ranges(self, word):
        word = word.replace('*', '[:]')
        ranges_start = word.find('[')
        if ranges_start < 0:
            yield self._get_hostname(word)
        else:
            ranges_end = word.find(']', ranges_start)
            prefix = word[:ranges_start]
            suffix = word[ranges_end + 1:]
            ranges = word[ranges_start + 1:ranges_end]
            for r in ranges.split(','):
                if r.find('..') >= 0:
                    pmin, pmax = r.split('..')
                    if pmax:
                        pmax = int(pmax) + 1
                    for name in self._get_hostnames('%s%%s%s' % (prefix, suffix), pmin, pmax):
                        yield name
                elif r.find(':') >= 0:
                    pmin, pmax = r.split(':')
                    for name in self._get_hostnames('%s%%s%s' % (prefix, suffix), pmin, pmax):
                        yield name
                else:
                    r = int(r)
                    for name in self._get_hostnames('%s%%s%s' % (prefix, suffix), r, r + 1):
                        yield name

    def _expand_alternatives(self, word):
        hosts = set()
        alt_start = word.find('{')
        if alt_start < 0:
            hosts.update(self._expand_ranges(word))
        else:
            alt_end = word.find('}', alt_start)
            prefix = word[:alt_start]
            suffix = word[alt_end + 1:]
            alternatives = word[alt_start + 1:alt_end]
            for alternative in alternatives.split('|'):
                hosts.update(self._expand_alternatives('%(prefix)s%(alternative)s%(suffix)s' % locals()))
        return hosts

    def expand(self, items):
        if items is None:
            raise ValueError("None value cannot be expanded.")
        if type(items) == str:
            items = [items]
        results = set()
        for item in items:
            for word in item.split():
                if word[0] in self.substract_prefix:
                    mode = '-'
                    word = word[1:]
                else:
                    mode = '+'

                hosts = set(self._expand_alternatives(word))

                if mode == '+':
                    results.update(hosts)
                else:
                    results.difference_update(hosts)
        return sorted(results)
