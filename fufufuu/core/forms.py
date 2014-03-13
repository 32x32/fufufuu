class BlankLabelSuffixMixin(object):

    def __init__(self, *args, **kwargs):
        if 'label_suffix' not in kwargs:
            kwargs['label_suffix'] = ''
        super().__init__(*args, **kwargs)
