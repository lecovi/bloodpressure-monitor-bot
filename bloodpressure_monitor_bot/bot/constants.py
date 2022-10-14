BLOODPRESSURE_REGEX_PATTERN = "(\d{2,3})\/(\d{2,3})( (\d{2,3}))?"
NEW_BLOODPRESSURE_REGEX_PATTERN="^(\d{2,3})\/(\d{2,3})( (\d{2,3}))?( (.*))?$"
DEVELOPER_CHAT_ID = 9691064
HELP_MESSAGE = """:robot: <strong>How to use this bot</strong> :question:

<b>Message Format</b>
- <code>sys/dia [hb]</code>: every time you message the bot with systolic/diastolic and heart beat pulse (<i>optional</i>) the bot will record in the spreadsheet.

<b>Commands:</b>
- /status: bot will share spreadsheet URL with number of records
- /last <code>[number=1]</code>: bot will share last records.
        <code>number</code> (<i>optional</i>) is used to share more than 1 record.
- /help: will print this message
- /cancel: cancel the conversation with the bot. You will need to /start again.
"""
MAIL, CREATE_SHEET, CONSENT, REGISTER_TA = range(4)