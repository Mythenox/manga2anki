from genanki import Model

DEFAULT_MODEL_VOCAB = Model(
    1427369726,
    "Default Vocab Model",
    fields=[
        {"name": "Surface"},
        {"name": "Reading"},
        {"name": "Meaning"},
        {"name": "Excerpt"},
    ],
    templates=[
        {
            "name": "Vocab",
            "qfmt": "{{Surface}}<br><br>{{Reading}}<br><br><hr>{{Excerpt}}",
            "afmt": "{{Surface}}<br><br>{{Reading}}<br><hr id=answer><br>{{Meaning}}<br><br><hr>{{Excerpt}}",
        }
    ],
    css="""
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        """,
)

DEFAULT_MODEL_KANJI = Model(
    1996218837,
    "Default Kanji Model",
    fields=[
        {"name": "Kanji"},
        {"name": "Reading"},
        {"name": "English Meaning"},
        {"name": "Contextual Surface"},
        {"name": "Contextual Reading"}
    ],
    templates=[
        {
            "name": "Kanji",
            "qfmt": "<div style='position: relative; right: 2%; font-size:15vw'>{{Kanji}}</div><hr>{{Contextual Surface}}",
            "afmt": """<div style='position: relative; right: 2%; font-size:15vw'>{{Kanji}}</div><br>{{Reading}}<br>{{English Meaning}}
                    <hr>{{Contextual Surface}}<br>{{Contextual Reading}}
            """,
        }
    ],
    css="""
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        """,
)