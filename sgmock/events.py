import datetime


def generate_for_create(sg, entity):
    project = entity.get('project')
    sg.create('EventLogEntry', {
        'event_type': 'Shotgun_%s_New' % entity['type'],
        'entity': entity,
        'project': project,
        'attribute_name': None,
        'meta': {
            'type': 'new_entity',
            'entity_type': entity['type'],
            'entity_id': entity['id']
        },
    }, _log=False, _generate_events=False)
    generate_for_update(sg, entity, None, extra_meta={'in_create': True})


def generate_for_update(sg, entity, old_values=None, new_values=None, extra_meta=None):
    project = entity.get('project')
    old_values = old_values or {}
    new_values = new_values or entity
    for key, new_value in new_values.iteritems():
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
            'entity': entity,
            'project': project,
            'attribute_name': key,
            'meta': meta,
        }, _log=False, _generate_events=False)


def generate_for_delete(sg, entity):

    project = entity.get('project')
    now = datetime.datetime.utcnow()

    # 1. change for retirement_date for the entity
    generate_for_update(sg, entity, new_values={'retirement_date': now})

    # 2. retirement event
    sg.create('EventLogEntry', {
        "attribute_name": None,
        'entity': entity,
        "event_type": "Shotgun_%s_Retirement" % entity['type'],
        "meta": {
            "type": "entity_retirement",
            'entity_type': entity['type'],
            'entity_id': entity['id'],
            "retirement_date": now.isoformat(),
        },
        'project': project,
    }, _log=False, _generate_events=False)

    # TODO:
    # 3. change events for entities that link to it

def generate_for_revive(sg, entity):

    project = entity.get('project')
    now = datetime.datetime.utcnow()

    # 1. change for retirement_date for the entity
    generate_for_update(sg, entity, new_values={'retirement_date': None})

    # 2. retirement event
    sg.create('EventLogEntry', {
        "event_type": "Shotgun_%s_Revival" % entity['type'],
        'entity': entity,
        'attribute_name': None,
        "meta": {
            'entity_type': entity['type'],
            'entity_id': entity['id'],
        },
        'project': project,
    }, _log=False, _generate_events=False)
