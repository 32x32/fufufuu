class Language:

    ENGLISH     = 'en'
    JAPANESE    = 'ja'

    choices = (
        ('en', 'English'),
        ('ja', '日本語'),
        ('de', 'Deutsch'),
        ('es', 'Español'),
        ('fr', 'Français'),
        ('ko', '한국어 '),
        ('pt', 'Português'),
        ('ru', 'русский язык'),
        ('th', 'ไทย'),
        ('vi', 'Tiếng Việt'),
        ('zh', '中文'),
        ('zz', 'Other'),
    )

    choices_dict = dict([(k, v) for k, v in choices])
