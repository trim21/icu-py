# -*- coding: utf-8 -*-
# ====================================================================
# Copyright (c) 2019 Open Source Applications Foundation.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# ====================================================================

import sys, os, six

from unittest import TestCase, main
from icu import *

class TestLocale(TestCase):

    def testConstructWithKeywords(self):

        l0 = Locale('fr', 'be', collation='phonebook', currency='euro')
        l1 = Locale('fr', 'be', '', 'collation=phonebook;currency=euro')

        self.assertEqual('fr_BE@collation=phonebook;currency=euro', str(l0))
        self.assertEqual('fr_BE@collation=phonebook;currency=euro', str(l1))
        self.assertEqual(l0, l1)

    def testCompare(self):

        af = Locale('af')
        mt = Locale('mt')
        zu = Locale('zu')

        self.assertLess(af, zu)
        self.assertFalse(mt < mt)
        self.assertFalse(zu < af)

        self.assertLessEqual(af, zu)
        self.assertLessEqual(mt, mt)
        self.assertFalse(zu <= af)

        self.assertEqual(mt, mt)
        self.assertFalse(af == zu)

        self.assertNotEqual(af, zu)
        self.assertFalse(mt != mt)

        self.assertGreater(zu, af)
        self.assertFalse(mt > mt)
        self.assertFalse(af > zu)

        self.assertGreaterEqual(zu, af)
        self.assertGreaterEqual(mt, mt)
        self.assertFalse(af >= zu)


if __name__ == "__main__":
    main()
