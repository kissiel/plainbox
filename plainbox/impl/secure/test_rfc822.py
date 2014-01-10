# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
#   Sylvain Pineau <sylvain.pineau@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
plainbox.impl.secure.rfc822
===========================

Test definitions for plainbox.impl.secure.rfc822 module
"""

from io import StringIO
from unittest import TestCase
import os

from plainbox.impl.secure.rfc822 import FileTextSource
from plainbox.impl.secure.rfc822 import Origin
from plainbox.impl.secure.rfc822 import PythonFileTextSource
from plainbox.impl.secure.rfc822 import RFC822Record
from plainbox.impl.secure.rfc822 import RFC822SyntaxError
from plainbox.impl.secure.rfc822 import UnknownTextSource
from plainbox.impl.secure.rfc822 import load_rfc822_records


class UnknownTextSourceTests(TestCase):
    """
    Tests for UnknownTextSource class
    """

    def setUp(self):
        self.src = UnknownTextSource()

    def test_str(self):
        """
        verify how UnknownTextSource. __str__() works
        """
        self.assertEqual(str(self.src), "???")

    def test_repr(self):
        """
        verify how UnknownTextSource.__repr__() works
        """
        self.assertEqual(repr(self.src), "UnknownTextSource()")

    def test_eq(self):
        """
        verify instances of UnknownTextSource are all equal to each other
        but not equal to any other object
        """
        other_src = UnknownTextSource()
        self.assertTrue(self.src == other_src)
        self.assertFalse(self.src == "???")

    def test_eq_others(self):
        """
        verify instances of UnknownTextSource are unequal to instances of other
        classes
        """
        self.assertTrue(self.src != object())
        self.assertFalse(self.src == object())

    def test_gt(self):
        """
        verify that instances of UnknownTextSource are not ordered
        """
        other_src = UnknownTextSource()
        self.assertFalse(self.src < other_src)
        self.assertFalse(other_src < self.src)

    def test_gt_others(self):
        """
        verify that instances of UnknownTextSource are not comparable to other
        objects
        """
        with self.assertRaises(TypeError):
            self.src < object()
        with self.assertRaises(TypeError):
            object() < self.src


class FileTextSourceTests(TestCase):
    """
    Tests for FileTextSource class
    """

    _FILENAME = "filename"

    def setUp(self):
        self.src = FileTextSource(self._FILENAME)

    def test_filename(self):
        """
        verify that FileTextSource.filename works
        """
        self.assertEqual(self._FILENAME, self.src.filename)

    def test_str(self):
        """
        verify that FileTextSource.__str__() works
        """
        self.assertEqual(str(self.src), self._FILENAME)

    def test_repr(self):
        """
        verify that FileTextSource.__repr__() works
        """
        self.assertEqual(repr(self.src), "FileTextSource('filename')")

    def test_eq(self):
        """
        verify that FileTextSource compares equal to other instances with the
        same filename and unequal to instances with different filenames.
        """
        self.assertTrue(FileTextSource('foo') == FileTextSource('foo'))
        self.assertTrue(FileTextSource('foo') != FileTextSource('bar'))

    def test_eq_others(self):
        """
        verify instances of FileTextSource are unequal to instances of other
        classes
        """
        self.assertTrue(FileTextSource('foo') != object())
        self.assertFalse(FileTextSource('foo') == object())

    def test_gt(self):
        """
        verify that FileTextSource is ordered by filename
        """
        self.assertTrue(
            FileTextSource("a") < FileTextSource("b") < FileTextSource("c"))
        self.assertTrue(
            FileTextSource("c") > FileTextSource("b") > FileTextSource("a"))

    def test_gt_others(self):
        """
        verify that instances of FileTextSource are not comparable to other
        objects
        """
        with self.assertRaises(TypeError):
            self.src < object()
        with self.assertRaises(TypeError):
            object() < self.src


class OriginTests(TestCase):

    def setUp(self):
        self.origin = Origin(FileTextSource("file.txt"), 10, 12)

    def test_smoke(self):
        self.assertEqual(self.origin.source.filename, "file.txt")
        self.assertEqual(self.origin.line_start, 10)
        self.assertEqual(self.origin.line_end, 12)

    def test_repr(self):
        expected = ("<Origin source:FileTextSource('file.txt')"
                    " line_start:10 line_end:12>")
        observed = repr(self.origin)
        self.assertEqual(expected, observed)

    def test_str(self):
        expected = "file.txt:10-12"
        observed = str(self.origin)
        self.assertEqual(expected, observed)

    def test_equal_operator(self):
        equal_origin = Origin(FileTextSource("file.txt"), 10, 12)
        self.assertEqual(self.origin, equal_origin)

    def test_comparison_operators_different_lines(self):
        unequal_origin_1 = Origin(FileTextSource("file.txt"), 10, 13)
        unequal_origin_2 = Origin(FileTextSource("file.txt"), 11, 12)
        unequal_origin_3 = Origin(FileTextSource("file.txt"), 10, 11)
        self.assertNotEqual(self.origin, unequal_origin_1)
        self.assertNotEqual(self.origin, unequal_origin_2)
        self.assertTrue(self.origin < unequal_origin_1)
        self.assertTrue(self.origin > unequal_origin_3)

    def test_comparison_operators_different_files(self):
        unequal_origin = Origin(FileTextSource("ghostfile.txt"), 10, 12)
        self.assertNotEqual(self.origin, unequal_origin)

    def test_origin_caller(self):
        """
        verify that Origin.get_caller_origin() uses PythonFileTextSource as the
        origin.source attribute.
        """
        self.assertIsInstance(
            Origin.get_caller_origin().source, PythonFileTextSource)

    def test_origin_source_filename_is_correct(self):
        """
        verify that make_job() can properly trace the filename of the python
        module that called make_job()
        """
        # Pass -1 to get_caller_origin() to have filename point at this file
        # instead of at whatever ends up calling the test method
        self.assertEqual(
            os.path.basename(Origin.get_caller_origin(-1).source.filename),
            "test_rfc822.py")


class RFC822RecordTests(TestCase):

    def test_smoke(self):
        data = {'key': 'value'}
        origin = Origin(FileTextSource('file.txt'), 1, 1)
        record = RFC822Record(data, origin)
        self.assertEqual(record.data, data)
        self.assertEqual(record.origin, origin)


class RFC822ParserTestsMixIn():

    loader = load_rfc822_records

    def test_empty(self):
        with StringIO("") as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 0)

    def test_single_record(self):
        with StringIO("key:value") as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'value'})

    def test_many_newlines(self):
        text = (
            "\n"
            "\n"
            "key1:value1\n"
            "\n"
            "\n"
            "\n"
            "key2:value2\n"
            "\n"
            "\n"
            "key3:value3\n"
            "\n"
            "\n"
        )
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].data, {'key1': 'value1'})
        self.assertEqual(records[1].data, {'key2': 'value2'})
        self.assertEqual(records[2].data, {'key3': 'value3'})

    def test_many_records(self):
        text = (
            "key1:value1\n"
            "\n"
            "key2:value2\n"
            "\n"
            "key3:value3\n"
        )
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].data, {'key1': 'value1'})
        self.assertEqual(records[1].data, {'key2': 'value2'})
        self.assertEqual(records[2].data, {'key3': 'value3'})

    def test_multiline_value(self):
        text = (
            "key:\n"
            " longer\n"
            " value\n"
        )
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'longer\nvalue'})

    def test_multiline_value_with_space(self):
        text = (
            "key:\n"
            " longer\n"
            " .\n"
            " value\n"
        )
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'longer\n\nvalue'})

    def test_multiline_value_with_period(self):
        text = (
            "key:\n"
            " longer\n"
            " ..\n"
            " value\n"
        )
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'longer\n.\nvalue'})

    def test_many_multiline_values(self):
        text = (
            "key1:initial\n"
            " longer\n"
            " value 1\n"
            "\n"
            "key2:\n"
            " longer\n"
            " value 2\n"
        )
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].data, {'key1': 'initial\nlonger\nvalue 1'})
        self.assertEqual(records[1].data, {'key2': 'longer\nvalue 2'})

    def test_irrelevant_whitespace(self):
        text = "key :  value  "
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'value'})

    def test_relevant_whitespace(self):
        text = (
            "key:\n"
            " value\n"
        )
        with StringIO(text) as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'value'})

    def test_bad_multiline(self):
        text = " extra value"
        with StringIO(text) as stream:
            with self.assertRaises(RFC822SyntaxError) as call:
                type(self).loader(stream)
            self.assertEqual(call.exception.msg, "Unexpected multi-line value")

    def test_garbage(self):
        text = "garbage"
        with StringIO(text) as stream:
            with self.assertRaises(RFC822SyntaxError) as call:
                type(self).loader(stream)
            self.assertEqual(call.exception.msg, "Unexpected non-empty line")

    def test_syntax_error(self):
        text = "key1 = value1"
        with StringIO(text) as stream:
            with self.assertRaises(RFC822SyntaxError) as call:
                type(self).loader(stream)
            self.assertEqual(call.exception.msg, "Unexpected non-empty line")

    def test_duplicate_error(self):
        text = (
            "key1: value1\n"
            "key1: value2\n"
        )
        with StringIO(text) as stream:
            with self.assertRaises(RFC822SyntaxError) as call:
                type(self).loader(stream)
            self.assertEqual(call.exception.msg, (
                "Job has a duplicate key 'key1' with old value 'value1'"
                " and new value 'value2'"))

    def test_origin_from_stream_is_Unknown(self):
        """
        verify that gen_rfc822_records() uses origin instances with source
        equal to UnknownTextSource, when no explicit source is provided and the
        stream has no name to infer a FileTextSource() from.
        """
        expected_origin = Origin(UnknownTextSource(), 1, 1)
        with StringIO("key:value") as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'value'})
        self.assertEqual(records[0].origin, expected_origin)

    def test_origin_from_filename_is_filename(self):
        # If the test's origin has a filename, we need a valid origin
        # with proper data.
        # We're faking the name by using a StringIO subclass with a
        # name property, which is how rfc822 gets that data.
        expected_origin = Origin(FileTextSource("file.txt"), 1, 1)
        with NamedStringIO("key:value",
                           fake_filename="file.txt") as stream:
            records = type(self).loader(stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].data, {'key': 'value'})
        self.assertEqual(records[0].origin, expected_origin)


class NamedStringIO(StringIO):
    """
     Subclass of StringIO with a name attribute.
     Use only for testing purposes, it's not guaranteed to be 100%
     compatible with StringIO.
    """
    def __init__(self, string, fake_filename=None):
        super(NamedStringIO, self).__init__(string)
        self._fake_filename = fake_filename

    @property
    def name(self):
        return(self._fake_filename)


class RFC822WriterTests(TestCase):
    """
    Tests for the :meth:`RFC822Record.dump()` method.
    """

    def test_single_record(self):
        with StringIO() as stream:
            RFC822Record({'key': 'value'}).dump(stream)
            self.assertEqual(stream.getvalue(), "key: value\n\n")

    def test_multiple_record(self):
        with StringIO() as stream:
            RFC822Record({'key1': 'value1', 'key2': 'value2'}).dump(stream)
            self.assertIn(
                stream.getvalue(), (
                    "key1: value1\nkey2: value2\n\n",
                    "key2: value2\nkey1: value1\n\n"))

    def test_multiline_value(self):
        text = (
            "key:\n"
            " longer\n"
            " value\n\n"
        )
        with StringIO() as stream:
            RFC822Record({'key': 'longer\nvalue'}).dump(stream)
            self.assertEqual(stream.getvalue(), text)

    def test_multiline_value_with_space(self):
        text = (
            "key:\n"
            " longer\n"
            " .\n"
            " value\n\n"
        )
        with StringIO() as stream:
            RFC822Record({'key': 'longer\n\nvalue'}).dump(stream)
            self.assertEqual(stream.getvalue(), text)

    def test_multiline_value_with_period(self):
        text = (
            "key:\n"
            " longer\n"
            " ..\n"
            " value\n\n"
        )
        with StringIO() as stream:
            RFC822Record({'key': 'longer\n.\nvalue'}).dump(stream)
            self.assertEqual(stream.getvalue(), text)

    def test_type_error(self):
        with StringIO() as stream:
            with self.assertRaises(AttributeError):
                RFC822Record(['key', 'value']).dump(stream)


class RFC822SyntaxErrorTests(TestCase):
    """
    Tests for RFC822SyntaxError class
    """

    def test_hash(self):
        """
        verify that RFC822SyntaxError is hashable
        """
        self.assertEqual(
            hash(RFC822SyntaxError("file.txt", 10, "msg")),
            hash(RFC822SyntaxError("file.txt", 10, "msg")))
