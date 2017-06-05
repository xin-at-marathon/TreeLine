#!/usr/bin/env python3

#******************************************************************************
# fieldformat.py, provides a class to handle field format types
#
# TreeLine, an information storage program
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#******************************************************************************

import re
import sys
import datetime
import xml.sax.saxutils as saxutils
import gennumber
import genboolean
import urltools
import globalref

fieldTypes = [N_('Text'), N_('HtmlText'), N_('OneLineText'), N_('SpacedText'),
              N_('Number'), N_('Date'), N_('Time'), N_('DateTime'),
              N_('Boolean'), N_('Choice'), N_('Combination'),
              N_('ExternalLink'), N_('InternalLink'), N_('RegularExpression')]
_errorStr = '#####'
_dateStampString = _('Now')
_timeStampString = _('Now')
_multipleSpaceRegEx = re.compile(r' {2,}')
linkRegExp = re.compile(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
linkSeparateNameRegExp = re.compile(r'(.*) \[(.*)\]\s*$')


class TextField:
    """Class to handle a rich-text field format type.

    Stores options and format strings for a text field type.
    Provides methods to return formatted data.
    """
    typeName = 'Text'
    defaultFormat = ''
    showRichTextInCell = True
    evalHtmlDefault = False
    fixEvalHtmlSetting = True
    defaultNumLines = 1
    editorClassName = 'RichTextEditor'
    formatHelpMenuList = []
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        self.name = name
        if not formatData:
            formatData = {}
        self.prefix = formatData.get('prefix', '')
        self.suffix = formatData.get('suffix', '')
        self.initDefault = formatData.get('init', '')
        self.numLines = formatData.get('lines', type(self).defaultNumLines)
        self.sortKeyNum = formatData.get('sortkeynum', 0)
        self.sortKeyForward = formatData.get('sortkeyfwd', True)
        self.evalHtml = self.evalHtmlDefault
        if not self.fixEvalHtmlSetting:
            self.evalHtml = formatData.get('evalhtml', self.evalHtmlDefault)
        self.useFileInfo = False
        self.showInDialog = True
        self.setFormat(formatData.get('format', type(self).defaultFormat))

    def formatData(self):
        """Return a dictionary of this field's format settings.
        """
        formatData = {'fieldname': self.name, 'fieldtype': self.typeName}
        if self.format:
            formatData['format'] = self.format
        if self.prefix:
            formatData['prefix'] = self.prefix
        if self.suffix:
            formatData['suffix'] = self.suffix
        if self.initDefault:
            formatData['init'] = self.initDefault
        if self.numLines != self.defaultNumLines:
            formatData['lines'] = self.numLines
        if self.sortKeyNum > 0:
            formatData['sortkeynum'] = self.sortKeyNum
        if not self.sortKeyForward:
            formatData['sortkeyfwd'] = False
        if (not self.fixEvalHtmlSetting and
            self.evalHtml != self.evalHtmlDefault):
            formatData['evalhtml'] = self.evalHtml
        return formatData

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Derived classes may raise a ValueError if the format is illegal.
        Arguments:
            format -- the new format string
        """
        self.format = format

    def outputText(self, node, titleMode, formatHtml):
        """Return formatted output text for this field in this node.

        Arguments:
            node -- the tree item storing the data
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        if self.useFileInfo:
            node = node.modelRef.fileInfoNode
        storedText = node.data.get(self.name, '')
        if storedText:
            return self.formatOutput(storedText, titleMode, formatHtml)
        return ''

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        prefix = self.prefix
        suffix = self.suffix
        if titleMode:
            storedText = removeMarkup(storedText)
            if formatHtml:
                prefix = removeMarkup(prefix)
                suffix = removeMarkup(suffix)
        elif not formatHtml:
            prefix = saxutils.escape(prefix)
            suffix = saxutils.escape(suffix)
        return '{0}{1}{2}'.format(prefix, storedText, suffix)

    def editorText(self, node):
        """Return text formatted for use in the data editor.

        The function for default text just returns the stored text.
        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        return self.formatEditorText(storedText)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        The function for default text just returns the stored text.
        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        return storedText

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        The function for default text field just returns the editor text.
        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        return editorText

    def storedTextFromTitle(self, titleText):
        """Return new text to be stored based on title text edits.

        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            titleText -- the new title text
        """
        return self.storedText(saxutils.escape(titleText))

    def getInitDefault(self):
        """Return the initial stored value for newly created nodes.
        """
        return self.initDefault

    def setInitDefault(self, editorText):
        """Set the default initial value from editor text.

        The function for default text field just returns the stored text.
        Arguments:
            editorText -- the new text entered into the editor
        """
        self.initDefault = self.storedText(editorText)

    def getEditorInitDefault(self):
        """Return initial value in editor format.

        The function for default text field just returns the initial value.
        """
        return self.formatEditorText(self.initDefault)

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return []

    def mathValue(self, node, zeroBlanks=True):
        """Return a value to be used in math field equations.

        Return None if blank and not zeroBlanks.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- accept blank field values if True
        """
        storedText = node.data.get(self.name, '')
        storedText = removeMarkup(storedText)
        return storedText if storedText or zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        storedText = removeMarkup(storedText)
        return storedText.lower()

    def sortKey(self, node):
        """Return a tuple with field type and comparison value for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('80_text', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Text version removes any markup and goes to lower case.
        Arguments:
            value -- the comparison value to adjust
        """
        value = removeMarkup(value)
        return value.lower()

    def changeType(self, newType):
        """Change this field's type to newType with a default format.

        Arguments:
            newType -- the new type name, excluding "Field"
        """
        self.__class__ = globals()[newType + 'Field']
        self.setFormat(self.defaultFormat)
        if self.fixEvalHtmlSetting:
            self.evalHtml = self.evalHtmlDefault

    def sepName(self):
        """Return the name enclosed with {* *} separators
        """
        if self.useFileInfo:
            return '{{*!{0}*}}'.format(self.name)
        return '{{*{0}*}}'.format(self.name)

    def getFormatHelpMenuList(self):
        """Return the list of descriptions and keys for the format help menu.
        """
        return self.formatHelpMenuList


class HtmlTextField(TextField):
    """Class to handle an HTML text field format type

    Stores options and format strings for an HTML text field type.
    Does not use the rich text editor.
    Provides methods to return formatted data.
    """
    typeName = 'HtmlText'
    showRichTextInCell = False
    evalHtmlDefault = True
    editorClassName = 'HtmlTextEditor'
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def storedTextFromTitle(self, titleText):
        """Return new text to be stored based on title text edits.

        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            titleText -- the new title text
        """
        return self.storedText(titleText)


class OneLineTextField(TextField):
    """Class to handle a single-line rich-text field format type.

    Stores options and format strings for a text field type.
    Provides methods to return formatted data.
    """
    typeName = 'OneLineText'
    editorClassName = 'OneLineTextEditor'
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        text = storedText.split('<br />', 1)[0]
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        return storedText.split('<br />', 1)[0]


class SpacedTextField(TextField):
    """Class to handle a preformatted text field format type.

    Stores options and format strings for a spaced text field type.
    Uses <pre> tags to preserve spacing.
    Does not use the rich text editor.
    Provides methods to return formatted data.
    """
    typeName = 'SpacedText'
    showRichTextInCell = False
    editorClassName = 'PlainTextEditor'
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        if storedText:
            storedText = '<pre>{0}</pre>'.format(storedText)
        return super().formatOutput(storedText, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Arguments:
            storedText -- the source text to format
        """
        return saxutils.unescape(storedText)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Arguments:
            editorText -- the new text entered into the editor
        """
        return saxutils.escape(editorText)

    def storedTextFromTitle(self, titleText):
        """Return new text to be stored based on title text edits.

        Arguments:
            titleText -- the new title text
        """
        return self.storedText(titleText)


class NumberField(HtmlTextField):
    """Class to handle a general number field format type.

    Stores options and format strings for a number field type.
    Provides methods to return formatted data.
    """
    typeName = 'Number'
    defaultFormat = '#.##'
    evalHtmlDefault = False
    editorClassName = 'LineEditor'
    formatHelpMenuList = [(_('Optional Digit\t#'), '#'),
                          (_('Required Digit\t0'), '0'),
                          (_('Digit or Space (external)\t<space>'), ' '),
                          ('', ''),
                          (_('Decimal Point\t.'), '.'),
                          (_('Decimal Comma\t,'), ','),
                          ('', ''),
                          (_('Comma Separator\t\,'), '\,'),
                          (_('Dot Separator\t\.'), '\.'),
                          (_('Space Separator (internal)\t<space>'), ' '),
                          ('', ''),
                          (_('Optional Sign\t-'), '-'),
                          (_('Required Sign\t+'), '+'),
                          ('', ''),
                          (_('Exponent (capital)\tE'), 'E'),
                          (_('Exponent (small)\te'), 'e')]

    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        try:
            text = gennumber.GenNumber(storedText).numStr(self.format)
        except ValueError:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        return gennumber.GenNumber(storedText).numStr(self.format)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not editorText:
            return ''
        return repr(gennumber.GenNumber().setFromStr(editorText, self.format))

    def mathValue(self, node, zeroBlanks=True):
        """Return a numeric value to be used in math field equations.

        Return None if blank and not zeroBlanks,
        raise a ValueError if it isn't a number.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- replace blank field values with zeros if True
        """
        storedText = node.data.get(self.name, '')
        if storedText:
            return gennumber.GenNumber(storedText).num
        return 0 if zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        try:
            return gennumber.GenNumber(storedText).num
        except ValueError:
            return 0

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('20_num', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Number version converts to a numeric value.
        Arguments:
            value -- the comparison value to adjust
        """
        try:
            return gennumber.GenNumber(value).num
        except ValueError:
            return 0


class DateField(HtmlTextField):
    """Class to handle a general date field format type.

    Stores options and format strings for a date field type.
    Provides methods to return formatted data.
    """
    typeName = 'Date'
    defaultFormat = '%B %-d, %Y'
    isoFormat = '%Y-%m-%d'
    evalHtmlDefault = False
    editorClassName = 'DateEditor'
    refDate = datetime.date(1970, 1, 1)
    formatHelpMenuList = [(_('Day (1 or 2 digits)\t%-d'), '%-d'),
                          (_('Day (2 digits)\t%d'), '%d'), ('', ''),
                          (_('Weekday Abbreviation\t%a'), '%a'),
                          (_('Weekday Name\t%A'), '%A'), ('', ''),
                          (_('Month (1 or 2 digits)\t%-m'), '%-m'),
                          (_('Month (2 digits)\t%m'), '%m'),
                          (_('Month Abbreviation\t%b'), '%b'),
                          (_('Month Name\t%B'), '%B'), ('', ''),
                          (_('Year (2 digits)\t%y'), '%y'),
                          (_('Year (4 digits)\t%Y'), '%Y'), ('', ''),
                          (_('Week Number (0 to 53)\t%-U'), '%-U'),
                          (_('Day of year (1 to 366)\t%-j'), '%-j')]
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        try:
            date = datetime.datetime.strptime(storedText,
                                              DateField.isoFormat).date()
            text = date.strftime(adjOutDateFormat(self.format))
        except ValueError:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        date = datetime.datetime.strptime(storedText,
                                          DateField.isoFormat).date()
        editorFormat = adjOutDateFormat(globalref.genOptions['EditDateFormat'])
        return date.strftime(editorFormat)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Two digit years are interpretted as 1950-2049.
        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        editorText = _multipleSpaceRegEx.sub(' ', editorText.strip())
        if not editorText:
            return ''
        editorFormat = adjInDateFormat(globalref.genOptions['EditDateFormat'])
        try:
            date = datetime.datetime.strptime(editorText, editorFormat).date()
        except ValueError:  # allow use of a 4-digit year to fix invalid dates
            fullYearFormat = editorFormat.replace('%y', '%Y')
            if fullYearFormat != editorFormat:
                date = datetime.datetime.strptime(editorText,
                                                  fullYearFormat).date()
        return date.strftime(DateField.isoFormat)

    def getInitDefault(self):
        """Return the initial stored value for newly created nodes.
        """
        if self.initDefault == _dateStampString:
            date = datetime.date.today()
            return date.strftime(DateField.isoFormat)
        return super().getInitDefault()

    def setInitDefault(self, editorText):
        """Set the default initial value from editor text.

        The function for default text field just returns the stored text.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if editorText == _dateStampString:
            self.initDefault = _dateStampString
        else:
            super().setInitDefault(editorText)

    def getEditorInitDefault(self):
        """Return initial value in editor format.

        The function for default text field just returns the initial value.
        """
        if self.initDefault == _dateStampString:
            return _dateStampString
        return super().getEditorInitDefault()

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return [_dateStampString]

    def mathValue(self, node, zeroBlanks=True):
        """Return a numeric value to be used in math field equations.

        Return None if blank and not zeroBlanks,
        raise a ValueError if it isn't a valid date.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- replace blank field values with zeros if True
        """
        storedText = node.data.get(self.name, '')
        if storedText:
            date = datetime.datetime.strptime(storedText,
                                              DateField.isoFormat).date()
            return (date - DateField.refDate).days
        return 0 if zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Date field uses ISO date format (YYY-MM-DD).
        Arguments:
            node -- the tree item storing the data
        """
        return node.data.get(self.name, '')

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('40_date', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Date version converts to an ISO date format (YYYY-MM-DD).
        Arguments:
            value -- the comparison value to adjust
        """
        value = _multipleSpaceRegEx.sub(' ', value.strip())
        if not value:
            return ''
        if value == _dateStampString:
            date = datetime.date.today()
            return date.strftime(DateField.isoFormat)
        try:
            return self.storedText(value)
        except ValueError:
            return value


class TimeField(HtmlTextField):
    """Class to handle a general time field format type

    Stores options and format strings for a time field type.
    Provides methods to return formatted data.
    """
    typeName = 'Time'
    defaultFormat = '%-I:%M:%S %p'
    isoFormat = '%H:%M:%S.%f'
    evalHtmlDefault = False
    editorClassName = 'TimeEditor'
    numChoiceColumns = 2
    autoAddChoices = False
    refTime = datetime.time()
    formatHelpMenuList = [(_('Hour (0-23, 1 or 2 digits)\t%-H'), '%-H'),
                          (_('Hour (00-23, 2 digits)\t%H'), '%H'),
                          (_('Hour (1-12, 1 or 2 digits)\t%-I'), '%-I'),
                          (_('Hour (01-12, 2 digits)\t%I'), '%I'), ('', ''),
                          (_('Minute (1 or 2 digits)\t%-M'), '%-M'),
                          (_('Minute (2 digits)\t%M'), '%M'), ('', ''),
                          (_('Second (1 or 2 digits)\t%-S'), '%-S'),
                          (_('Second (2 digits)\t%S'), '%S'), ('', ''),
                          (_('Microseconds (6 digits)\t%f'), '%f'), ('', ''),
                          (_('AM/PM\t%p'), '%p')]
    def __init__(self, name, attrs=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            attrs -- the attributes that define this field's format
        """
        super().__init__(name, attrs)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        try:
            time = datetime.datetime.strptime(storedText,
                                              TimeField.isoFormat).time()
            text = time.strftime(adjOutDateFormat(self.format))
        except ValueError:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        time = datetime.datetime.strptime(storedText,
                                          TimeField.isoFormat).time()
        editorFormat = adjOutDateFormat(globalref.genOptions['EditTimeFormat'])
        return time.strftime(editorFormat)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        editorText = _multipleSpaceRegEx.sub(' ', editorText.strip())
        if not editorText:
            return ''
        editorFormat = adjInDateFormat(globalref.genOptions['EditTimeFormat'])
        time = None
        try:
            time = datetime.datetime.strptime(editorText, editorFormat).time()
        except ValueError:
            noSecFormat = editorFormat.replace(':%S', '')
            noSecFormat = _multipleSpaceRegEx.sub(' ', noSecFormat.strip())
            try:
                time = datetime.datetime.strptime(editorText,
                                                  noSecFormat).time()
            except ValueError:
                for altFormat in (editorFormat, noSecFormat):
                    noAmFormat = altFormat.replace('%p', '')
                    noAmFormat = _multipleSpaceRegEx.sub(' ',
                                                         noAmFormat.strip())
                    try:
                        time = datetime.datetime.strptime(editorText,
                                                          noAmFormat).time()
                        break
                    except ValueError:
                        pass
                if not time:
                    raise ValueError
        return time.strftime(TimeField.isoFormat)

    def annotatedComboChoices(self, editorText):
        """Return a list of (choice, annotation) tuples for the combo box.

        Arguments:
            editorText -- the text entered into the editor
        """
        editorFormat = adjOutDateFormat(globalref.genOptions['EditTimeFormat'])
        choices = [(datetime.datetime.now().time().strftime(editorFormat),
                    '({0})'.format(_timeStampString))]
        for hour in (6, 9, 12, 15, 18, 21, 0):
            choices.append((datetime.time(hour).strftime(editorFormat), ''))
        return choices

    def getInitDefault(self):
        """Return the initial stored value for newly created nodes.
        """
        if self.initDefault == _timeStampString:
            time = datetime.datetime.now().time()
            return time.strftime(TimeField.isoFormat)
        return super().getInitDefault()

    def setInitDefault(self, editorText):
        """Set the default initial value from editor text.

        The function for default text field just returns the stored text.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if editorText == _timeStampString:
            self.initDefault = _timeStampString
        else:
            super().setInitDefault(editorText)

    def getEditorInitDefault(self):
        """Return initial value in editor format.

        The function for default text field just returns the initial value.
        """
        if self.initDefault == _timeStampString:
            return _timeStampString
        return super().getEditorInitDefault()

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return [_timeStampString]

    def mathValue(self, node, zeroBlanks=True):
        """Return a numeric value to be used in math field equations.

        Return None if blank and not zeroBlanks,
        raise a ValueError if it isn't a valid time.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- replace blank field values with zeros if True
        """
        storedText = node.data.get(self.name, '')
        if storedText:
            time = datetime.datetime.strptime(storedText,
                                              TimeField.isoFormat).time()
            return (time - TimeField.refTime).seconds
        return 0 if zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Time field uses HH:MM:SS format.
        Arguments:
            node -- the tree item storing the data
        """
        return node.data.get(self.name, '')

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('50_time', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Time version converts to HH:MM:SS format.
        Arguments:
            value -- the comparison value to adjust
        """
        value = _multipleSpaceRegEx.sub(' ', value.strip())
        if not value:
            return ''
        if value == _timeStampString:
            time = datetime.datetime.now().time()
            return time.strftime(TimeField.isoFormat)
        try:
            return self.storedText(value)
        except ValueError:
            return value


class DateTimeField(HtmlTextField):
    """Class to handle a general date and time field format type.

    Stores options and format strings for a date and time field type.
    Provides methods to return formatted data.
    """
    typeName = 'DateTime'
    defaultFormat = '%B %-d, %Y %-I:%M:%S %p'
    isoFormat = '%Y-%m-%d %H:%M:%S.%f'
    evalHtmlDefault = False
    editorClassName = 'DateTimeEditor'
    refDateTime = datetime.datetime(1970, 1, 1)
    formatHelpMenuList = [(_('Day (1 or 2 digits)\t%-d'), '%-d'),
                          (_('Day (2 digits)\t%d'), '%d'), ('', ''),
                          (_('Weekday Abbreviation\t%a'), '%a'),
                          (_('Weekday Name\t%A'), '%A'), ('', ''),
                          (_('Month (1 or 2 digits)\t%-m'), '%-m'),
                          (_('Month (2 digits)\t%m'), '%m'),
                          (_('Month Abbreviation\t%b'), '%b'),
                          (_('Month Name\t%B'), '%B'), ('', ''),
                          (_('Year (2 digits)\t%y'), '%y'),
                          (_('Year (4 digits)\t%Y'), '%Y'), ('', ''),
                          (_('Week Number (0 to 53)\t%-U'), '%-U'),
                          (_('Day of year (1 to 366)\t%-j'), '%-j'),
                          (_('Hour (0-23, 1 or 2 digits)\t%-H'), '%-H'),
                          (_('Hour (00-23, 2 digits)\t%H'), '%H'),
                          (_('Hour (1-12, 1 or 2 digits)\t%-I'), '%-I'),
                          (_('Hour (01-12, 2 digits)\t%I'), '%I'), ('', ''),
                          (_('Minute (1 or 2 digits)\t%-M'), '%-M'),
                          (_('Minute (2 digits)\t%M'), '%M'), ('', ''),
                          (_('Second (1 or 2 digits)\t%-S'), '%-S'),
                          (_('Second (2 digits)\t%S'), '%S'), ('', ''),
                          (_('Microseconds (6 digits)\t%f'), '%f'), ('', ''),
                          (_('AM/PM\t%p'), '%p')]
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        try:
            dateTime = datetime.datetime.strptime(storedText,
                                                  DateTimeField.isoFormat)
            text = dateTime.strftime(adjOutDateFormat(self.format))
        except ValueError:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        dateTime = datetime.datetime.strptime(storedText,
                                              DateTimeField.isoFormat)
        editorFormat = '{0} {1}'.format(globalref.genOptions['EditDateFormat'],
                                        globalref.genOptions['EditTimeFormat'])
        editorFormat = adjOutDateFormat(editorFormat)
        return dateTime.strftime(editorFormat)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Two digit years are interpretted as 1950-2049.
        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        editorText = _multipleSpaceRegEx.sub(' ', editorText.strip())
        if not editorText:
            return ''
        editorFormat = '{0} {1}'.format(globalref.genOptions['EditDateFormat'],
                                        globalref.genOptions['EditTimeFormat'])
        editorFormat = adjInDateFormat(editorFormat)
        dateTime = None
        try:
            dateTime = datetime.datetime.strptime(editorText, editorFormat)
        except ValueError:
            noSecFormat = editorFormat.replace(':%S', '')
            noSecFormat = _multipleSpaceRegEx.sub(' ', noSecFormat.strip())
            altFormats = [editorFormat, noSecFormat]
            for altFormat in altFormats[:]:
                noAmFormat = altFormat.replace('%p', '')
                noAmFormat = _multipleSpaceRegEx.sub(' ', noAmFormat.strip())
                altFormats.append(noAmFormat)
            for altFormat in altFormats[:]:
                fullYearFormat = altFormat.replace('%y', '%Y')
                altFormats.append(fullYearFormat)
            for editorFormat in altFormats[1:]:
                try:
                    dateTime = datetime.datetime.strptime(editorText,
                                                          editorFormat)
                    break
                except ValueError:
                    pass
            if not dateTime:
                raise ValueError
        return dateTime.strftime(DateTimeField.isoFormat)

    def getInitDefault(self):
        """Return the initial stored value for newly created nodes.
        """
        if self.initDefault == _timeStampString:
            dateTime = datetime.datetime.now()
            return dateTime.strftime(DateTimeField.isoFormat)
        return super().getInitDefault()

    def setInitDefault(self, editorText):
        """Set the default initial value from editor text.

        The function for default text field just returns the stored text.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if editorText == _timeStampString:
            self.initDefault = _timeStampString
        else:
            super().setInitDefault(editorText)

    def getEditorInitDefault(self):
        """Return initial value in editor format.

        The function for default text field just returns the initial value.
        """
        if self.initDefault == _timeStampString:
            return _timeStampString
        return super().getEditorInitDefault()

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return [_timeStampString]

    def mathValue(self, node, zeroBlanks=True):
        """Return a numeric value to be used in math field equations.

        Return None if blank and not zeroBlanks,
        raise a ValueError if it isn't a valid time.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- replace blank field values with zeros if True
        """
        storedText = node.data.get(self.name, '')
        if storedText:
            dateTime = datetime.datetime.strptime(storedText,
                                                  DateTimeField.isoFormat)
            return (dateTime - DateTimeField.refDateTime).seconds
        return 0 if zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        DateTime field uses YYYY-MM-DD HH:MM:SS format.
        Arguments:
            node -- the tree item storing the data
        """
        return node.data.get(self.name, '')

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('45_datetime', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Time version converts to HH:MM:SS format.
        Arguments:
            value -- the comparison value to adjust
        """
        value = _multipleSpaceRegEx.sub(' ', value.strip())
        if not value:
            return ''
        if value == _timeStampString:
            dateTime = datetime.datetime.now()
            return dateTime.strftime(DateTimeField.isoFormat)
        try:
            return self.storedText(value)
        except ValueError:
            return value


class ChoiceField(HtmlTextField):
    """Class to handle a field with pre-defined, individual text choices.

    Stores options and format strings for a choice field type.
    Provides methods to return formatted data.
    """
    typeName = 'Choice'
    editSep = '/'
    defaultFormat = '1/2/3/4'
    evalHtmlDefault = False
    fixEvalHtmlSetting = False
    editorClassName = 'ComboEditor'
    numChoiceColumns = 1
    autoAddChoices = False
    formatHelpMenuList = [(_('Separator\t/'), '/'), ('', ''),
                          (_('"/" Character\t//'), '//'), ('', ''),
                          (_('Example\t1/2/3/4'), '1/2/3/4')]
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Arguments:
            format -- the new format string
        """
        super().setFormat(format)
        self.choiceList = self.splitText(self.format)
        if self.evalHtml:
            self.choices = set(self.choiceList)
        else:
            self.choices = set([saxutils.escape(choice) for choice in
                                self.choiceList])

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        if storedText not in self.choices:
            storedText = _errorStr
        return super().formatOutput(storedText, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if storedText and storedText not in self.choices:
            raise ValueError
        if self.evalHtml:
            return storedText
        return saxutils.unescape(storedText)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not self.evalHtml:
            editorText = saxutils.escape(editorText)
        if not editorText or editorText in self.choices:
            return editorText
        raise ValueError

    def comboChoices(self):
        """Return a list of choices for the combo box.
        """
        return self.choiceList

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return self.choiceList

    def splitText(self, textStr):
        """Split textStr using editSep, return a list of strings.

        Double editSep's are not split (become single).
        Removes duplicates and empty strings.
        Arguments:
            textStr -- the text to split
        """
        result = []
        textStr = textStr.replace(self.editSep * 2, '\0')
        for text in textStr.split(self.editSep):
            text = text.strip().replace('\0', self.editSep)
            if text and text not in result:
                result.append(text)
        return result


class CombinationField(ChoiceField):
    """Class to handle a field with multiple pre-defined text choices.

    Stores options and format strings for a combination field type.
    Provides methods to return formatted data.
    """
    typeName = 'Combination'
    editorClassName = 'CombinationEditor'
    numChoiceColumns = 2
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Arguments:
            format -- the new format string
        """
        TextField.setFormat(self, format)
        if not self.evalHtml:
            format = saxutils.escape(format)
        self.choiceList = self.splitText(format)
        self.choices = set(self.choiceList)
        self.outputSep = ''

    def outputText(self, node, titleMode, formatHtml):
        """Return formatted output text for this field in this node.

        Sets output separator prior to calling base class methods.
        Arguments:
            node -- the tree item storing the data
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        self.outputSep = node.nodeFormat().outputSeparator
        return super().outputText(node, titleMode, formatHtml)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        selections, valid = self.sortedSelections(storedText)
        if valid:
            result = self.outputSep.join(selections)
        else:
            result = _errorStr
        return TextField.formatOutput(self, result, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        selections = set(self.splitText(storedText))
        if selections.issubset(self.choices):
            if self.evalHtml:
                return storedText
            return saxutils.unescape(storedText)
        raise ValueError

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not self.evalHtml:
            editorText = saxutils.escape(editorText)
        selections, valid = self.sortedSelections(editorText)
        if not valid:
            raise ValueError
        return self.joinText(selections)

    def comboChoices(self):
        """Return a list of choices for the combo box.
        """
        if self.evalHtml:
            return self.choiceList
        return [saxutils.unescape(text) for text in self.choiceList]

    def comboActiveChoices(self, editorText):
        """Return a sorted list of choices currently in editorText.

        Arguments:
            editorText -- the text entered into the editor
        """
        selections, valid = self.sortedSelections(saxutils.escape(editorText))
        if self.evalHtml:
            return selections
        return [saxutils.unescape(text) for text in selections]

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return []

    def sortedSelections(self, inText):
        """Split inText using editSep and sort like format string.

        Return a tuple of resulting selection list and bool validity.
        Valid if all choices are in the format string.
        Arguments:
            inText -- the text to split and sequence
        """
        selections = set(self.splitText(inText))
        result = [text for text in self.choiceList if text in selections]
        return (result, len(selections) == len(result))

    def joinText(self, textList):
        """Join the text list using editSep, return the string.

        Any editSep in text items become double.
        Arguments:
            textList -- the list of text items to join
        """
        return self.editSep.join([text.replace(self.editSep, self.editSep * 2)
                                  for text in textList])


class BooleanField(ChoiceField):
    """Class to handle a general boolean field format type.

    Stores options and format strings for a boolean field type.
    Provides methods to return formatted data.
    """
    typeName = 'Boolean'
    defaultFormat = _('yes/no')
    evalHtmlDefault = False
    fixEvalHtmlSetting = True
    formatHelpMenuList = [(_('true/false'), 'true/false'),
                          (_('T/F'), 'T/F'), ('', ''),
                          (_('yes/no'), 'yes/no'),
                          (_('Y/N'), 'Y/N'), ('', ''),
                          ('1/0', '1/0')]
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        try:
            text =  genboolean.GenBoolean(storedText).boolStr(self.format)
        except ValueError:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        return genboolean.GenBoolean(storedText).boolStr(self.format)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not editorText:
            return ''
        try:
            return repr(genboolean.GenBoolean().setFromStr(editorText,
                                                           self.format))
        except ValueError:
            return repr(genboolean.GenBoolean(editorText))

    def mathValue(self, node, zeroBlanks=True):
        """Return a value to be used in math field equations.

        Return None if blank and not zeroBlanks,
        raise a ValueError if it isn't a valid boolean.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- replace blank field values with zeros if True
        """
        storedText = node.data.get(self.name, '')
        if storedText:
            return genboolean.GenBoolean(storedText).value
        return False if zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Bool fields return True or False values.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        try:
            return genboolean.GenBoolean(storedText).value
        except ValueError:
            return False

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('30_bool', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Bool version converts to a bool value.
        Arguments:
            value -- the comparison value to adjust
        """
        try:
            return genboolean.GenBoolean().setFromStr(value, self.format).value
        except ValueError:
            try:
                return genboolean.GenBoolean(value).value
            except ValueError:
                return False


class ExternalLinkField(HtmlTextField):
    """Class to handle a field containing various types of external HTML links.

    Protocol choices include http, https, file, mailto.
    Stores data as HTML tags, shows in editors as "protocol:address [name]".
    """
    typeName = 'ExternalLink'
    evalHtmlDefault = False
    editorClassName = 'ExtLinkEditor'

    def __init__(self, name, attrs=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            attrs -- the attributes that define this field's format
        """
        super().__init__(name, attrs)

    def addressAndName(self, storedText):
        """Return the link title and the name from the given stored link.

        Raise ValueError if the stored text is not formatted as a link.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ('', '')
        linkMatch = linkRegExp.search(storedText)
        if not linkMatch:
            raise ValueError
        address, name = linkMatch.groups()
        return (address, name)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        if titleMode:
            linkMatch = linkRegExp.search(storedText)
            if linkMatch:
                address, name = linkMatch.groups()
                storedText = name.strip()
                if not storedText:
                    storedText = address.lstrip('#')
        return super().formatOutput(storedText, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        address, name = self.addressAndName(storedText)
        name = name.strip()
        if not name:
            name = urltools.shortName(address)
        return '{0} [{1}]'.format(address, name)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not editorText:
            return ''
        nameMatch = linkSeparateNameRegExp.match(editorText)
        if nameMatch:
            address, name = nameMatch.groups()
        else:
            address = editorText
            name = urltools.shortName(address)
        return '<a href="{0}">{1}</a>'.format(address.strip(), name.strip())

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Link fields use link address.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        if not storedText:
            return ''
        try:
            address, name = self.addressAndName(storedText)
        except ValueError:
            return storedText
        return address.lstrip('#').lower()

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('60_link', self.compareValue(node))


class InternalLinkField(ExternalLinkField):
    """Class to handle a field containing internal links to nodes.

    Stores data as HTML local link tag, shows in editors as "id [name]".
    """
    typeName = 'InternalLink'
    editorClassName = 'IntLinkEditor'

    def __init__(self, name, attrs=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            attrs -- the attributes that define this field's format
        """
        super().__init__(name, attrs)

    def editorText(self, node):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Also raises a ValueError if the link is not a valid destination, with
        the editor text as the second argument to the exception.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        return self.formatEditorText(storedText, node.treeStructureRef())

    def formatEditorText(self, storedText, treeStructRef):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Also raises a ValueError if the link is not a valid destination, with
        the editor text as the second argument to the exception.
        Arguments:
            storedText -- the source text to format
            treeStructRef -- ref to the tree structure to get the linked title
        """
        if not storedText:
            return ''
        address, name = self.addressAndName(storedText)
        address = address.lstrip('#')
        targetNode = treeStructRef.nodeDict.get(address, None)
        linkTitle = targetNode.title() if targetNode else _errorStr
        name = name.strip()
        if not name and targetNode:
            name = linkTitle
        result = 'LinkTo: {0} [{1}]'.format(linkTitle, name)
        if linkTitle == _errorStr:
            raise ValueError('invalid address', result)
        return result

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Uses the "address [name]" format as input, not the final editor form.
        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new editor text in "address [name]" format
        """
        print(editorText)
        if not editorText:
            return ''
        nameMatch = linkSeparateNameRegExp.match(editorText)
        if not nameMatch:
            raise ValueError
        address, name = nameMatch.groups()
        return '<a href="#{0}">{1}</a>'.format(address.strip(), name.strip())

    def getEditorInitDefault(self):
        """Return initial value in editor format.

        The function for default text field just returns the initial value.
        """
        if not self.initDefault:
            return ''
        linkMatch = linkRegExp.search(self.initDefault)
        if not linkMatch:
            raise ValueError
        address, name = linkMatch.groups()
        if not name:
            name = _errorStr
        return 'LinkTo: {0} [{1}]'.format(_errorStr, name)


class RegularExpressionField(HtmlTextField):
    """Class to handle a field format type controlled by a regular expression.

    Stores options and format strings for a number field type.
    Provides methods to return formatted data.
    """
    typeName = 'RegularExpression'
    defaultFormat = '.*'
    evalHtmlDefault = False
    fixEvalHtmlSetting = False
    editorClassName = 'LineEditor'
    formatHelpMenuList = [(_('Any Character\t.'), '.'),
                          (_('End of Text\t$'), '$'),
                          ('', ''),
                          (_('0 Or More Repetitions\t*'), '*'),
                          (_('1 Or More Repetitions\t+'), '+'),
                          (_('0 Or 1 Repetitions\t?'), '?'),
                          ('', ''),
                          (_('Set of Numbers\t[0-9]'), '[0-9]'),
                          (_('Lower Case Letters\t[a-z]'), '[a-z]'),
                          (_('Upper Case Letters\t[A-Z]'), '[A-Z]'),
                          (_('Not a Number\t[^0-9]'), '[^0-9]'),
                          ('', ''),
                          (_('Or\t|'), '|'),
                          (_('Escape a Special Character\t\\'), '\\')]

    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Raise a ValueError if the format is illegal.
        Arguments:
            format -- the new format string
        """
        try:
            re.compile(format)
        except re.error:
            raise ValueError
        super().setFormat(format)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        match = re.match(self.format, saxutils.unescape(storedText))
        if not storedText or match:
            text = storedText
        else:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not self.evalHtml:
            storedText = saxutils.unescape(storedText)
        match = re.match(self.format, storedText)
        if not storedText or match:
            return storedText
        raise ValueError

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        match = re.match(self.format, editorText)
        if not editorText or match:
            if self.evalHtml:
                return editorText
            return saxutils.escape(editorText)
        raise ValueError


####  Utility Functions  ####

_stripTagRe = re.compile('<.*?>')

def removeMarkup(text):
    """Return text with all HTML Markup removed and entities unescaped.
    """
    text = _stripTagRe.sub('', text)
    return saxutils.unescape(text)

def adjOutDateFormat(dateFormat):
    """Replace Linux lead zero removal with Windows version in date formats.

    Arguments:
        dateFormat -- the format to modify
    """
    if sys.platform.startswith('win'):
        dateFormat = dateFormat.replace('%-', '%#')
    return dateFormat

def adjInDateFormat(dateFormat):
    """Remove lead zero formatting in date formats for reading dates.

    Arguments:
        dateFormat -- the format to modify
    """
    return dateFormat.replace('%-', '%')
