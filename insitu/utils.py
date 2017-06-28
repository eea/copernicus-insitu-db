ALL_OPTIONS_LABEL = 'All'


def get_choices(field, model_cls=None, objects=None):
    model_values = []
    if model_cls:
        model_values = list(model_cls.objects.values_list(field, flat=True))
    elif objects:
        model_values = list(objects.values_list(field, flat=True))
    return [ALL_OPTIONS_LABEL] + model_values
