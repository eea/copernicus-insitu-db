ALL_OPTIONS_LABEL = 'All'


def get_choices(model_cls, field):
    model_values = list(model_cls.objects.values_list(field, flat=True))
    return [ALL_OPTIONS_LABEL] + model_values


def get_choices_filtered(objects, field):
    model_values = list(objects.values_list(field, flat=True))
    return [ALL_OPTIONS_LABEL] + model_values
