import os

import audeer
import audformat


build_dir = audeer.mkdir('../build')

db = audformat.Database(
    name='ir-c4dm',
    author='Rebecca Stewart, Mark Sandler',
    organization='Centre for Digital Music, Queen Mary, University of London',
    license='CC-BY-NC-4.0',
    source=(
        'http://isophonics.net/content/room-impulse-response-data-set'
    ),
    usage='research',
    description=(
        'This collection of room impulse responses '
        'was measured in the Great Hall, '
        'the Octagon, '
        'and a classroom at the Mile End campus '
        'of Queen Mary, University of London in 2008. '
        'The measurements were created using the sine sweep technique '
        'with a Genelec 8250A loudspeaker '
        'and two microphones, '
        'an omnidirectional DPA 4006 '
        'and a B-format Soundfield SPS422B. '
        'Only the omnidirectional recordings are included in ths=is release. '
        'When using any portion of this data set, cite: '
        'Stewart, Rebecca and Sandler, Mark. '
        '"Database of Omnidirectional and B-Format Impulse Responses", '
        'in Proc. of IEEE Int. Conf. on Acoustics, '
        'Speech, and Signal Processing (ICASSP 2010), '
        'Dallas, Texas, March 2010.'
    ),
)

# Media
db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=96000,
    channels=1,
)

# Schemes
db.schemes['x'] = audformat.Scheme(
    'float',
    description=(
        'Lateral position with loudspeaker at 0m. '
        'Negative values are positoned left '
        'of the loudspeaker when facing the microphone '
        'from the loudspeakers position.'
    ),
)
db.schemes['y'] = audformat.Scheme(
    'float',
    description=(
        'Longitudinal position with loudspeaker at 0m. '
    ),
)
db.schemes['room'] = audformat.Scheme(
    labels={
        'classroom': (
            'A set of 130 IRs were taken '
            'within a classroom in the '
            'School of Electronic Engineering and Computer Science. '
            'The room measures roughly 7.5 x 9 x 3.5 m (236 cubic m) '
            'with reflective surfaces of a linoleum floor, '
            'painted plaster walls and ceiling, '
            'and a large whiteboard. '
            'When in use for lectures the room is filled with desks '
            'and chairs. '
            'These were stacked '
            'and moved to the side against the windows '
            'during the measurements. '
            'Measurements are 50 cm apart '
            'arranged in 10 rows and 13 columns '
            'relative to the speaker, '
            'with the 8th column directly on axis with the speaker.'
        ),
        'greathall': (
            'The Great Hall is a multipurpose hall '
            'that can hold approximately 800 seats. '
            'The hall has a stage and seating areas on the floor '
            'and a balcony. '
            'The microphones were placed in the seating area '
            'on the floor, '
            'roughly a 23 m x 16 m area, '
            'which was cleared of chairs. '
            'The microphone positions are identical'
            'to the layout for the Octagon, '
            '169 IRs over a 12 m x 12 m area. '
            'The room is significantly bigger '
            'than the measuring area '
            'as the balcony extends 20 m past the rear wall.'
        ),
        'octagon': (
            'The Octagon is a Victorian building completed in 1888 '
            'and originally designed to be a library. '
            'It is currently used as a conference venue, '
            'but the walls are still lined with books '
            'with a wooden floor and plaster ceiling. '
            'As the name suggests, '
            'the room has eight walls '
            'each 7.5 m in length '
            'and a domed ceiling reaching 21 m over the floor, '
            'with an approximate volume of 9500 cubic m. '
            'A set of 169 IRs were measured in the centre of the room.'
        ),
    },
    description='Recording room',
)


# Prepare data
def x_mapping(file, room):
    if room == 'classroom':
        x = float(file[0:2])
        return (x - 30) / 10
    else:
        x = float(file[1:3])
        return x - 6


def y_mapping(file, room):
    if room == 'classroom':
        y = float(file[3:5])
        return (y + 15) / 10
    else:
        y = float(file[4:6])
        return y + 2


files = []
rooms = []
xs = []
ys = []
for room in db.schemes['room'].labels:
    room_files = audeer.list_file_names(
        os.path.join(build_dir, room, 'omni'),
        basenames=True,
    )
    xs += [x_mapping(f, room) for f in room_files]
    ys += [y_mapping(f, room) for f in room_files]
    rooms += [room] * len(room_files)
    files += [f'{room}/omni/{f}' for f in room_files]


# Tables
index = audformat.filewise_index(files)
db['files'] = audformat.Table(index)
db['files']['room'] = audformat.Column(scheme_id='room')
db['files']['room'].set(rooms)
db['files']['x'] = audformat.Column(scheme_id='x')
db['files']['x'].set(xs)
db['files']['y'] = audformat.Column(scheme_id='y')
db['files']['y'].set(ys)

db.save(build_dir)
