
def generate_for_create(sg, entity):
    project = entity.get('project')
    sg.create('EventLogEntry', {
        'event_type': 'Shotgun_%s_New' % entity['type'],
        'entity': sg._minimal_copy(entity),
        'project': sg._minimal_copy(project) if project else None,
        'attribute_name': None,
        'meta': {
            'type': 'new_entity',
            'entity_type': entity['type'],
            'entity_id': entity['id']
        },
    }, _log=False, _generate_events=False)
    generate_for_update(sg, entity, None, {'in_create': True})


def generate_for_update(sg, entity, old_values=None, extra_meta=None):
    project = entity.get('project')
    old_values = old_values or {}
    for key, new_value in entity.iteritems():
        if key in ('type', 'id', 'created_at', 'updated_at', 'created_by', 'updated_by'):
            continue
        old_value = old_values.get(key)
        meta = {
            'type': 'attribute_change',
            'entity_type': entity['type'],
            'entity_id': entity['id'],
            'attribute_name': key,
            'field_data_type': 'color', # TODO
            'new_value': new_value,
            'old_value': old_values,
        }
        meta.update(extra_meta or {})
        sg.create('EventLogEntry', {
            'event_type': 'Shotgun_%s_Change' % entity['type'],
            'entity': sg._minimal_copy(entity),
            'project': sg._minimal_copy(project) if project else None,
            'attribute_name': key,
            'meta': meta,
        }, _log=False, _generate_events=False)
