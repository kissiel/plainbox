# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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
:mod:`plainbox.impl.unit.category` -- category unit
===================================================

Categories are a way of associating tests with a human-readable "group".
Particular job definitions can say that they belong to a specific group
(using the category_id field). The display value of that group is loaded
from a particular category unit. This way any provider can extend the list
of categories and we can reliably fix typos and translate the actual names
in a compatible way.
"""

import logging

from plainbox.i18n import gettext as _
from plainbox.impl import deprecated
from plainbox.impl.symbol import SymbolDef
from plainbox.impl.unit import UnitWithId
from plainbox.impl.unit import UnitWithIdValidator
from plainbox.impl.validation import Problem
from plainbox.impl.validation import ValidationError


logger = logging.getLogger("plainbox.unit.category")


class CategoryUnitValidator(UnitWithIdValidator):
    """
    Validator for :class:`CategoryUnit` units.
    """

    def validate(self, unit, strict=False, deprecated=False):
        """
        Validate the specified category

        :param unit:
            :class:`CategoryUnit` to validate
        :param strict:
            Enforce strict validation. Non-conforming categories will be
            rejected. This is off by default to ensure that non-critical errors
            don't prevent categories from being used.
        :param deprecated:
            Enforce deprecation validation. Categories having deprecated fields
            will be rejected. This is off by default to allow backwards
            compatible categories to be used without any changes.
        """
        # Check basic stuff
        super().validate(unit, strict=strict, deprecated=deprecated)
        # Check if name is empty
        if unit.name is None:
            raise ValidationError(CategoryUnit.fields.name, Problem.missing)


class CategoryUnit(UnitWithId):
    """
    Test Category Unit

    This unit defines testing categories. Job defintions can be associated
    with at most one category.
    """

    @classmethod
    def instantiate_template(cls, data, raw_data, origin, provider,
                             parameters, field_offset_map):
        """
        Instantiate this unit from a template.

        The point of this method is to have a fixed API, regardless of what the
        API of a particular unit class ``__init__`` method actually looks like.

        It is easier to standardize on a new method that to patch all of the
        initializers, code using them and tests to have an uniform initializer.
        """
        # This assertion is a low-cost trick to ensure that we override this
        # method in all of the subclasses to ensure that the initializer is
        # called with correctly-ordered arguments.
        assert cls is CategoryUnit, \
            "{}.instantiate_template() not customized".format(cls.__name__)
        return cls(data, raw_data, origin, provider, parameters,
                   field_offset_map)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<CategoryUnit id:{!r} name:{!r}>".format(self.id, self.name)

    class fields(SymbolDef):
        """
        Symbols for each field that a JobDefinition can have
        """
        id = 'id'
        name = 'name'

    def tr_unit(self):
        """
        Translated (optionally) value of the unit field (overridden)

        The return value is always 'category' (translated)
        """
        return _("category")

    @deprecated("0.7", "call unit.tr_unit() instead")
    def get_unit_type(self):
        return _("category")

    @property
    def name(self):
        return self.get_record_value('name')

    def tr_name(self):
        return self.get_translated_record_value("name")

    def validate(self, **validation_kwargs):
        """
        Validate this job definition

        :param validation_kwargs:
            Keyword arguments to pass to the
            :meth:`CategoryUnitValidator.validate()`
        :raises ValidationError:
            If the category has any problems.
        """
        return CategoryUnitValidator().validate(self, **validation_kwargs)

    class Meta(UnitWithId.Meta):

        template_constraints = dict(UnitWithId.Meta.template_constraints)
        template_constraints.update({
            # The name field should vary so that instantiated categories
            # have different user-visible names
            'name': 'vary',
        })