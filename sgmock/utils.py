
def is_entity(e):
    return isinstance(e, dict) and e.get('type') and e.get('id')

def minimize(input_):

    if is_entity(input_):
        return {'type': input_['type'], 'id': input_['id']}

    if isinstance(input_, dict):
        return dict((key, minimize(v)) for k, v in input_.iteritems())

    if isinstance(input_, (list, tuple)):
        return tuple(minimize(x) for x in input_)

    return input_
