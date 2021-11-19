{
    'name': 'Project Task Timesheet Activities - Begin/End Hours',
    'version': '14.0.1.0.4',
    'author': 'Vertel AB',
    'contributors': 'Verified Email Europe AB,Hemangi Rupareliya,Vertel AB,',
    'website': 'https://vertel.se/',
    'license': 'AGPL-3',
    'category': 'Tools',
    'description': '''
    Here is video for that: https://www.loom.com/share/58f0c25d1aed4f4b8b41dcd6ce5ab4b8 \n 
    ''', 
    'depends': [
        'hr_timesheet_activity_begin_end' #https://github.com/OCA/timesheet/tree/14.0/hr_timesheet_activity_begin_end
    ],
    'data': {
        'views/project_views.xml'
    },
    'application': False,
    'installable': True,
}
