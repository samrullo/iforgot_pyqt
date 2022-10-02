from distutils.command.config import config
import pathlib

def populate_colorful_label_stle(app_ctxt):
    colors=["orange","blue","black"]
    colorful_label_styles=[]
    styles_folder=pathlib.Path(app_ctxt.get_resource("styles"))
    label_styles_file=styles_folder/"colorful_labels.qss"
    for color in colors:
        colorful_label_template=f"""QLabel#big_lbl_orange{{
                                    font:bold 30px 'Arial';
                                    color:{color};
                                    }}"""
        colorful_label_styles.append(colorful_label_template)
    label_styles_file.write_text("\n".join(colorful_label_styles))
    return label_styles_file