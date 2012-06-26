#!/usr/bin/env python

import unittest
import re

from datetime import datetime
from dateutil import tz, parser
from sys import path

path.append('./')
path.append('../')
import har

################################################################################
# Meta Test Cases
################################################################################

class HarObjectTest(unittest.TestCase):

    def setUp(self):
        self.skipTest("This is a test that is applied to other tests")

    def test_default_init_(self):
        self.obj()

    def test_empty_init_(self):
        self.obj(empty=True)

    def test_validate_missing_values(self):
        for missing_values_json in ['{}']:
            self.assertRaises(har.MissingValueException,
                              self.obj,
                              missing_values_json)

    def test_validate_bad_json(self):
        #check if invalid json fails
        invalid_json = 'z'
        self.assertRaises(ValueError, self.obj, invalid_json)


################################################################################
# Test Cases
################################################################################

class TestHarEncoder(unittest.TestCase):

    def setUp(self):
        self.har_encoder = har.HarEncoder()
        self.iso8601_re = re.compile(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?\+\d{2}:\d{2}')

    def test_date_decoding(self):
        good_json = '2009-07-24T19:20:30.45+01:00'
        good_dt = datetime(2009, 07, 24,
                           19, 20, 30, 450000,
                           tz.tzoffset(None, 3600))
        test_json = self.har_encoder.default(good_dt)
        g_match = re.match(self.iso8601_re, good_json)
        t_match = re.match(self.iso8601_re, test_json)
        #This isn't a great test... we should have a better one
        self.assertTrue(g_match)
        self.assertTrue(t_match)

    def test_date_encoding(self):
        good_json = '2009-07-24T19:20:30.45+01:00'
        good_dt = datetime(2009, 07, 24,
                           19, 20, 30, 450000,
                           tz.tzoffset(None, 3600))
        test_dt = parser.parse(good_json)
        self.assertEqual(good_dt, test_dt)

    def test_setting_tz(self):
        no_tz = datetime.now()
        gmt = no_tz.replace(tzinfo= tz.tzoffset(None, 0))
        har.TIMEZONE = tz.tzoffset(None, 0)
        good_json = self.har_encoder.default(gmt)
        test_json = self.har_encoder.default(no_tz)
        self.assertEqual(good_json, test_json)


class test__MetaHar(unittest.TestCase):

    def test___init__(self):
        #Should not ever instantiate.
        with self.assertRaises(AssertionError):
            har._MetaHar()

class test__KeyValueHar(unittest.TestCase):

    def test__init__(self):
        #Should not ever instantiate.
        with self.assertRaises(AssertionError):
            har._KeyValueHar()

class TestHarContainer(HarObjectTest):

    def setUp(self):
        self.obj = har.HarContainer

    def test_default_repr__(self):
        expected = r"<HarContainer: ('log',)>"
        har_container = self.obj()
        self.assertEqual(expected, har_container.__repr__())

    def test_empty_repr__(self):
        expected = r"<HarContainer: (empty)>"
        har_container = self.obj(empty=True)
        self.assertEqual(expected, har_container.__repr__())
        
    def test_validate_good(self):
        #make sure good stuff works
        good_json = ('{"log": {"version": "1.2", "creator":'
                     '{"version": "$Id$", "name": "Harpy"}, '
                     '"entries": []}}')
        har_container = self.obj(good_json)

    def test_validate_bad_json(self):        
        #check if invalid json fails
        invalid_json = 'z'
        self.assertRaises(ValueError, self.obj, invalid_json)
        
    def test_validate_bad_types(self):
        for bad_types_json in ['{"log": {}}',
                               '{"log":[]}',
                               '{"log":1}',
                               '{"log":"x"}',
                               ]:
            self.assertRaises(har.ValidationError,
                              self.obj,
                              bad_types_json)
            #add more validation tests...

class TestLog(HarObjectTest):

    def setUp(self):
        self.obj = har.Log

    def test_default_repr_(self):
        expected = "<HAR 1.2 Log created by Harpy $Id$: ('entries', 'version', 'creator')>"
        log = self.obj()
        self.assertEqual(expected, log.__repr__())

    def test_empty_repr_(self):
        expected = "<Log object not fully initilized>"
        log = self.obj(empty=True)
        self.assertEqual(expected, log.__repr__())

    def test_validate_good(self):
        #make sure good stuff works
        good_json = ('{"version": "1.2", "creator":'
                     '{"version": "$Id$", "name": "Harpy"}, '
                     '"entries": []}')
        log = self.obj(good_json)

    def test_validate_bad_types(self):
        for bad_types_json in [('{"version": 1.2, "creator":'
                                '{"version": "$Id$", "name": "Harpy"}, '
                                '"entries": []}'),
                               '{"version": 1.2, "creator":[], "entries": []}',
                               ('{"version": "1.2", "creator":[], "entries": 1}'),
                               ]:
            self.assertRaises(har.ValidationError,
                              self.obj,
                              bad_types_json)

class TestCreator(HarObjectTest):

    def setUp(self):
        self.obj = har.Creator

    def test_default_repr_(self):
        expected = "<Created by Harpy: ('version', 'name')>"
        creator = har.Creator()
        self.assertEqual(expected, creator.__repr__())

    def test_empty_repr_(self):
        expected = r"<Created by [uninitialized]: (empty)>"
        creator = har.Creator(empty=True)
        self.assertEqual(expected, creator.__repr__())

    def test_validate_good(self):
        #make sure good stuff works
        good_json = '{"version": "$Id$", "name": "Harpy"}'
        har.Creator(good_json)

    def test_validate_bad_types(self):
        for bad_types_json in ['{"version": 3, "name": "Harpy"}',
                               '{"version": "$Id$", "name": 3}'
                               ]:
            self.assertRaises(har.ValidationError,
                              har.Creator,
                              bad_types_json)

class TestBrowser(TestCreator):

    def setUp(self):
        self.obj = har.Browser

    def test_default_repr_(self):
        expected = "<Browser 'Harpy': ('version', 'name') >"
        obj = self.obj()
        self.assertEqual(expected, obj.__repr__())

    def test_empty_repr_(self):
        expected = r"<Browser '[uninitialized]': (empty) >"
        obj = self.obj(empty=True)
        self.assertEqual(expected, obj.__repr__())

class TestPage(HarObjectTest):

    def setUp(self):
        self.obj = har.Page
    
    def test_default_repr__(self):
        expected = r"<Page with title '[Title could not be determined]': ('pageTimings', 'title')>"
        page = self.obj()
        self.assertEqual(expected, page.__repr__())

    def test_empty_repr__(self):
        expected = r"<Page with title '[undefined]': (empty)>"
        har_container = self.obj(empty=True)
        self.assertEqual(expected, har_container.__repr__())

    def test_validate_good(self):
        #make sure good stuff works
        good_json = '{"id": "1", "startedDateTime": "2012-06-25T22:50:54.188477-07:00", "pageTimings": {}, "title": "Test Page"}'
        har.Page(good_json)

    def test_validate_bad_types(self):
        for bad_types_json in ['{"id": null, "startedDateTime": "2012-06-25T22:50:54.188477-07:00", "pageTimings": {}, "title": "Test Page"}',
                               '{"id": null, "startedDateTime": "2012-06-25T22:50:54.188477-07:00", "pageTimings": {}, "title": 2}'
                               ]:
            self.assertRaises(har.ValidationError,
                              har.Page,
                              bad_types_json)

    #!!! need to add a test that a non-uniq page cannot be added to an entry

class TestPageTimings(HarObjectTest):

    def setUp(self):
        self.obj = har.PageTimings

    def test__repr__(self): #no values are required
        expected = r"<Page timing : (empty)>"
        obj = self.obj(empty=True)
        self.assertEqual(expected, obj.__repr__())

    def test_validate(self):
        # page_timings = PageTimings()
        # self.assertEqual(expected, page_timings.validate())
        assert False # TODO: implement your test here

class TestEntry(HarObjectTest):

    def setUp(self):
        self.obj = har.Entry

    def test_default_repr__(self): #no values are required
        expected = r""
        obj = self.obj(empty=True)
        self.assertEqual(expected, obj.__repr__())

    def test_empty_repr__(self): #no values are required
        expected = r"<Page timing : (empty)>"
        obj = self.obj(empty=True)
        self.assertEqual(expected, obj.__repr__())

    def test_validate(self):
        # entry = Entry()
        # self.assertEqual(expected, entry.validate())
        assert False # TODO: implement your test here

    def test_uniq(self):
        # add test for uniq
        # entry = Entry()
        # self.assertEqual(expected, entry.validate())
        assert False # TODO: implement your test here
        

class TestRequest(HarObjectTest):
    def test___repr__(self):
        # request = Request()
        # self.assertEqual(expected, request.__repr__())
        assert False # TODO: implement your test here

    def test_devour(self):
        # request = Request()
        # self.assertEqual(expected, request.devour(req, proto, comment, keep_b64_raw))
        assert False # TODO: implement your test here

    def test_puke(self):
        # request = Request()
        # self.assertEqual(expected, request.puke())
        assert False # TODO: implement your test here

    def test_render(self):
        # request = Request()
        # self.assertEqual(expected, request.render())
        assert False # TODO: implement your test here

    def test_set_defaults(self):
        # request = Request()
        # self.assertEqual(expected, request.set_defaults())
        assert False # TODO: implement your test here

    def test_set_header(self):
        # request = Request()
        # self.assertEqual(expected, request.set_header(name, value))
        assert False # TODO: implement your test here

    def test_validate(self):
        # request = Request()
        # self.assertEqual(expected, request.validate())
        assert False # TODO: implement your test here

class TestResponse(HarObjectTest):
    def test___repr__(self):
        # response = Response()
        # self.assertEqual(expected, response.__repr__())
        assert False # TODO: implement your test here

    def test_devour(self):
        # response = Response()
        # self.assertEqual(expected, response.devour(res, proto, comment, keep_b64_raw))
        assert False # TODO: implement your test here

    def test_puke(self):
        # response = Response()
        # self.assertEqual(expected, response.puke())
        assert False # TODO: implement your test here

    def test_render(self):
        # response = Response()
        # self.assertEqual(expected, response.render())
        assert False # TODO: implement your test here

    def test_validate(self):
        # response = Response()
        # self.assertEqual(expected, response.validate())
        assert False # TODO: implement your test here

class TestCookie(HarObjectTest):
    def test___repr__(self):
        # cookie = Cookie()
        # self.assertEqual(expected, cookie.__repr__())
        assert False # TODO: implement your test here

    def test_devour(self):
        # cookie = Cookie()
        # self.assertEqual(expected, cookie.devour(cookie_string))
        assert False # TODO: implement your test here

    def test_validate(self):
        # cookie = Cookie()
        # self.assertEqual(expected, cookie.validate())
        assert False # TODO: implement your test here

class TestPostData(HarObjectTest):
    def test_validate(self):
        # post_data = PostData()
        # self.assertEqual(expected, post_data.validate())
        assert False # TODO: implement your test here

class TestParam(HarObjectTest):
    def test___repr__(self):
        # param = Param()
        # self.assertEqual(expected, param.__repr__())
        assert False # TODO: implement your test here

    def test_validate(self):
        # param = Param()
        # self.assertEqual(expected, param.validate())
        assert False # TODO: implement your test here

class TestContent(HarObjectTest):
    def test___repr__(self):
        # content = Content()
        # self.assertEqual(expected, content.__repr__())
        assert False # TODO: implement your test here

    def test_validate(self):
        # content = Content()
        # self.assertEqual(expected, content.validate())
        assert False # TODO: implement your test here

class TestCache(HarObjectTest):
    def test___repr__(self):
        # cache = Cache()
        # self.assertEqual(expected, cache.__repr__())
        assert False # TODO: implement your test here

    def test_validate(self):
        # cache = Cache()
        # self.assertEqual(expected, cache.validate())
        assert False # TODO: implement your test here

class TestRequestCache(HarObjectTest):
    def test_validate(self):
        # request_cache = RequestCache()
        # self.assertEqual(expected, request_cache.validate())
        assert False # TODO: implement your test here

class TestTimings(HarObjectTest):
    def test___repr__(self):
        # timings = Timings()
        # self.assertEqual(expected, timings.__repr__())
        assert False # TODO: implement your test here

    def test_validate(self):
        # timings = Timings()
        # self.assertEqual(expected, timings.validate())
        assert False # TODO: implement your test here

class TestTest(HarObjectTest):
    def test_test(self):
        # self.assertEqual(expected, test())
        assert False # TODO: implement your test here

class TestUsage(unittest.TestCase):
    def test_usage(self):
        expected = "usage: %s (docs|test)\n\n" % "test"
        expected += ("Either print out documentation "
                     "for this module or run a test.")
        self.assertEqual(expected, har.usage("test"))

# class TestFullLoadFromFile(unittest.TestCase):

#     def load_ssb(self):
#         tests


if __name__ == '__main__':
    unittest.main()
