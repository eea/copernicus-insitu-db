ALL_OPTIONS_LABEL = 'All'


def get_choices(model_cls, field):
    model_values = list(model_cls.objects.values_list(field, flat=True))
    return [ALL_OPTIONS_LABEL] + model_values
