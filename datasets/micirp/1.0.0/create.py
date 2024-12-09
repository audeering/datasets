import os
import shutil

import pandas as pd

import audeer
import audformat


def main():
    description = (
        'The Microphone Impulse Response Project (MicIRP) contains '
        'impulse response data for vintage microphones. '
        'The impulse response files were created using the analysis '
        'software Fuzzmeasure. '
        'The microphones were tested using a swept-sine method '
        'in a small booth, treated with much acoustic foam, '
        'placed about 20 to 30 cm from the source. '
        'Although the recording system and booth are calibrated '
        'regularly with a Beyerdynamic measurement microphone, there '
        'are problems comparing, for example, a figure-8 ribbon '
        'with an omnidirectional standard, as they will see different '
        'amounts of reflections from the side. '
        'So, it should be noted that the impulse response files describe '
        'the microphones measured in the booth, rather than in free space.'
    )
    languages = []
    db = audformat.Database(
        name='micirp',
        source='http://micirp.blogspot.com/',
        usage=audformat.define.Usage.COMMERCIAL,
        description=description,
        license=audformat.define.License.CC_BY_SA_4_0,
        languages=languages,
        author=(
            'Stewart Tavener (Xaudia.com)'
        ),
    )
    current_dir = os.path.dirname(__file__)
    build_dir = audeer.mkdir(os.path.join(current_dir, './build'))
    audio_dir = 'dirs'
    audio_path = os.path.join(current_dir, audio_dir)

    file_list = audeer.list_file_names(audio_path, recursive=True)
    rel_file_list = [
        os.path.join(
            audio_dir,
            os.path.split(file)[1]
        )
        for file in file_list
    ]

    manufacturers = [
        'AKG', 'Altec', 'American', 'Amperite', 'Astatic', 'B&O', 'BBC', 'Beyer', 'Coles', 'Doremi',
        'Electrovoice', 'EMI', 'Film Industries', 'Foster', 'Framez', 'Gaumont-Kalee', 'GEC', 'Grampian',
        'HMV', 'Lomo', 'Marconi', 'Meazzi', 'Melodium', 'Oktava', 'RCA',
        'Reslo', 'Shure', 'Sony', 'STC', 'Telefunken', 'Toshiba'
    ]
    manufacturer_map = {
        'BandO': 'B&O', 'Beomic': 'B&O', 'EV': 'Electrovoice', 'FilmIndustries': 'Film Industries',
        'GaumontKalee': 'Gaumont-Kalee',
    }
    for manufacturer in manufacturers:
        manufacturer_map[manufacturer] = manufacturer

    def get_manufacturer(filename):
        for k, v in manufacturer_map.items():
            if k in filename:
                return v

    df = pd.DataFrame(index=audformat.filewise_index(rel_file_list))
    df['manufacturer'] = df.index.to_series().apply(get_manufacturer)
    db.schemes['manufacturer'] = audformat.Scheme(
        labels=manufacturers, description='The manufacturer of the microphone that was recorded.'
    )
    db['files'] = audformat.Table(
        index=df.index
    )
    db['files']['manufacturer'] = audformat.Column(
        scheme_id='manufacturer'
    )
    db['files']['manufacturer'].set(df['manufacturer'])
    if not os.path.exists(os.path.join(build_dir, audio_dir)):
        shutil.copytree(
            audio_path,
            os.path.join(build_dir, audio_dir)
        )
    db.save(build_dir)


if __name__ == '__main__':
    main()
