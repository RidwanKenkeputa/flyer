import streamlit as st
from flyer import Flyer
from PIL import Image
import io
import os



st.set_page_config(page_title="Flyer Builder Studio", layout="wide")

st.title("Flyer Builder Studio")
st.write("Design your flyer without writing code. Just upload and configure using the approved template.")


# -------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------
if "back_list" not in st.session_state:
    st.session_state.back_list = []

if "front_list" not in st.session_state:
    st.session_state.front_list = []

if "other_list" not in st.session_state:
    st.session_state.other_list = []

if "footer_list" not in st.session_state:
    st.session_state.footer_list = []

if "flyer_generated" not in st.session_state:
    st.session_state.flyer_generated = False



# SIDEBAR: FLYER TYPE CONFIGURATION
# -------------------------------
# st.sidebar.header("Enter your Token")
# remove_bg_api_key = st.sidebar.text_input("Enter your RemoveBG API Token")
remove_bg_api_key = None


st.sidebar.header("Flyer Type Selection")
flyer_type = st.sidebar.selectbox("Choose Flyer Type", ["phone", "laptop"], index=0)


# -------------------------------
# SIDEBAR: BASIC CONFIGURATION
# -------------------------------
st.sidebar.header("Flyer Settings")

image_types = ["png", "jpg", "jpeg", "bmp", "tiff", "tif", "gif", "webp", "heif", "heic"]
bg_img = st.sidebar.file_uploader("Background Image", type=image_types)
logo_img = st.sidebar.file_uploader("Logo", type=image_types)

title_text = st.sidebar.text_input("Title", "Enter the product name or title here")
subtitle_text = st.sidebar.text_input("Subtitle", "Colour:")
subtitle_desc = st.sidebar.text_area("Subtitle Description",
                                     "Enter the colour description")


st.sidebar.header("Font Settings")

# Load fonts
font_folder = "./fonts"
available_fonts = [f for f in os.listdir(font_folder) if f.lower().endswith(".ttf")]

# Preset colors
preset_colors = {"Black": "#000000", "Red": "#FF0000", "Green": "#00FF00"}

# Parts to configure (super short format)
parts = [
    ("Title", "Poppins-Black.ttf", 200),
    ("Subheader", "Poppins-Regular.ttf", 150),
    ("Subheader Description", "Poppins-Regular.ttf", 90),
    ("Body", "Poppins-Regular.ttf", 90),
]

font_settings = {}

def font_section(name, default_font, default_size):
    with st.sidebar.expander(name, expanded=False):
        # Font name
        index = available_fonts.index(default_font) if default_font in available_fonts else 0
        font_name = os.path.join(font_folder, st.selectbox("Font", available_fonts, index=index, key=name+"_font"))
        
        # Font size
        font_size = st.slider("Size", 30, 300, default_size, 5, key=name+"_size")

        # Font color
        font_color = st.color_picker("Color", "#000000", key=f"{name}_color")

        return {"font": font_name, "size": font_size, "color": font_color}

# Build all sections in 4 lines
for name, default_font, default_size in parts:
    font_settings[name] = font_section(name, default_font, default_size)





# -------------------------------
# MAIN UI LAYOUT
# -------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Flyer Body Images")

    use_two_columns = st.radio(
        "Do you want two columns design?", 
        options=["Yes", "No"]
    )

    use_two_columns = True if use_two_columns == "Yes" else False

    if use_two_columns == "Yes":
        st.write("Two-column layout selected")
    else:
        st.write("Single-column layout selected")

    # ---- MAIN BACK IMAGES ----
    if flyer_type == "phone":  # Only show this section if flyer type is "phone"
        with st.expander("Main Back Images"):
            if st.button("Add Back Image"):
                st.session_state.back_list.append(len(st.session_state.back_list))

            for idx in st.session_state.back_list:
                file = st.file_uploader(f"Back View Image {idx+1}", type=image_types, key=f"back{idx}")
                if st.button(f"Remove Back {idx+1}", key=f"remove_back{idx}"):
                    st.session_state.back_list.remove(idx)



    # ---- MAIN FRONT IMAGES ----
    with st.expander("Main Front Images"):
        if st.button("Add Front Image"):
            st.session_state.front_list.append(len(st.session_state.front_list))

        for idx in st.session_state.front_list:
            file = st.file_uploader(f"Front View Image {idx+1}", type=image_types, key=f"front{idx}")
            if st.button(f"Remove Front {idx+1}", key=f"remove_front{idx}"):
                st.session_state.front_list.remove(idx)


    # ---- OTHER SIDE IMAGES ----
    is_vertical = False

    if use_two_columns:
        with st.expander("Other Images (Side / Extra)"):
            is_vertical = st.radio(
                "Arrange side images vertically?",
                options=[True, False]
            )

            if st.button("Add Other Image"):
                st.session_state.other_list.append(len(st.session_state.other_list))

            for idx in st.session_state.other_list:
                file = st.file_uploader(f"Other Image {idx+1}", type=image_types, key=f"other{idx}")
                if st.button(f"Remove Other {idx+1}", key=f"remove_other{idx}"):
                    st.session_state.other_list.remove(idx)


    # ---- FOOTER ----
    st.header("Flyer Footer Items")

    with st.expander("Footer Icons + Text"):
        if st.button("Add Footer Item"):
            st.session_state.footer_list.append(len(st.session_state.footer_list))

        for idx in st.session_state.footer_list:
            icon = st.file_uploader(f"Footer Icon {idx+1}", type=image_types, key=f"footer_icon{idx}")
            txt = st.text_input(f"Footer Text {idx+1}", key=f"footer_txt{idx}")
            if st.button(f"Remove Footer {idx+1}", key=f"remove_footer{idx}"):
                st.session_state.footer_list.remove(idx)


with col2:
    st.header("Flyer Preview")

    if st.button("Generate Flyer"):
        error_message = ""
        if not bg_img:
            error_message += "Please upload a background image."

        if not bg_img:
            error_message += "Please upload a background image. "

        if not title_text or not subtitle_text:
            error_message += "Please enter a title and subtitle. "

        if not any([st.session_state.back_list, st.session_state.front_list, st.session_state.other_list]):
            error_message += "Please upload at least one back, front, or other image. "

        if error_message:
            st.error(error_message)

        else:
            bg_img
            # Save temporary background
            bg_temp = "temp_bg.png"
            Image.open(bg_img).save(bg_temp)


            title_font            = font_settings["Title"]["font"]
            title_font_size       = font_settings["Title"]["size"]
            title_font_fill       = font_settings["Title"]["color"]

            body_font             = font_settings["Body"]["font"]
            body_font_size        = font_settings["Body"]["size"]
            body_font_fill        = font_settings["Body"]["color"]

            subheader_font        = font_settings["Subheader"]["font"]
            subheader_font_size   = font_settings["Subheader"]["size"]
            subheader_font_fill   = font_settings["Subheader"]["color"]

            subheader_desc_font        = font_settings["Subheader Description"]["font"]
            subheader_desc_font_size   = font_settings["Subheader Description"]["size"]
            subheader_desc_font_fill   = font_settings["Subheader Description"]["color"]

            flyer = Flyer(
                        bg_temp,
                        title_font, title_font_size, title_font_fill,
                        body_font, body_font_size, body_font_fill,
                        subheader_font, subheader_font_size, subheader_font_fill,
                        subheader_desc_font, subheader_desc_font_size, subheader_desc_font_fill,
                        flyer_type=flyer_type, vertical=is_vertical,
                        remove_bg_api_key = remove_bg_api_key
                    )

            # Apply logo
            if logo_img:
                temp_logo = "temp_logo.png"
                Image.open(logo_img).save(temp_logo)
                flyer.fix_logo(temp_logo)

            # Title + Subtitle
            flyer.create_title(title_text)
            flyer.create_subtitle(subtitle_text, subtitle_desc)

            # Body - back
            for idx in st.session_state.back_list:
                f = st.session_state.get(f"back{idx}")
                if f:
                    path = f"temp_back_{idx}.png"
                    Image.open(f).save(path)
                    flyer.fit_body(path, 'back', 'main')

            # Body - front
            for idx in st.session_state.front_list:
                f = st.session_state.get(f"front{idx}")
                if f:
                    path = f"temp_front_{idx}.png"
                    Image.open(f).save(path)
                    flyer.fit_body(path, 'front', 'main')

            # Body - others
            for idx in st.session_state.other_list:
                f = st.session_state.get(f"other{idx}")
                if f:
                    path = f"temp_other_{idx}.png"
                    Image.open(f).save(path)
                    flyer.fit_body(path, part="other")

            flyer.create_body(column=use_two_columns)

            # FOOTER
            for idx in st.session_state.footer_list:
                icon = st.session_state.get(f"footer_icon{idx}")
                txt = st.session_state.get(f"footer_txt{idx}", "")
                if icon:
                    temp_icon = f"temp_footer_{idx}.png"
                    Image.open(icon).save(temp_icon)
                    flyer.fit_footer(temp_icon, txt)

            flyer.create_footer()

            # Show output
            st.success("Flyer generated!")
            st.image(flyer.background, width='stretch')

            # Download
            buf = io.BytesIO()
            flyer.background.save(buf, format="PNG")
            st.download_button("Download Flyer", data=buf.getvalue(), file_name="flyer.png")

            # Mark flyer as generated
            st.session_state.flyer_generated = True


        # else:
        #     st.error("Upload a background image first!")

    # ------------------------------------------------
    # RESET BUTTON (Visible only after flyer is generated)
    # ------------------------------------------------
    if st.session_state.flyer_generated:
        if st.button("Reset App"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
