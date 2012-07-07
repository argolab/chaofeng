from chaofeng import loader

fileloader = {
    ".tpl":loader.load_templete,
    ".txt":loader.load_text,
    ".seq":loader.load_sequence,
    ".ani":loader.load_animation,
    }

static = {
    "root":"./static",
    "loader":fileloader,
    "encoding":"utf8"
    }
