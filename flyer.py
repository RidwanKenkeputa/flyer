from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO


### Set the text background box width to be dynamic
class Flyer:
    def __init__(self, bg_name, title_font, title_font_size, title_font_fill, body_font, body_font_size, body_font_fill,
                 subheader_font, subheader_font_size, subheader_font_fill, subheader_desc_font, subheader_desc_font_size,
                 subheader_desc_font_fill, flyer_type="phone", vertical=False, remove_bg_api_key=None):  # Default to "phone" flyer type
        self.background = Image.open(bg_name)
        self.footer_img_list = {}
        self.body_imgs = {}
        self.title_font = title_font
        self.title_font_size = title_font_size
        self.title_font_fill = title_font_fill
        self.body_font = body_font
        self.body_font_size = body_font_size
        self.body_font_fill = body_font_fill
        self.subheader_font = subheader_font
        self.subheader_font_fill = subheader_font_fill
        self.subheader_font_size = subheader_font_size
        self.subheader_desc_font = subheader_desc_font
        self.subheader_desc_font_size = subheader_desc_font_size
        self.subheader_desc_font_fill = subheader_desc_font_fill
        self.flyer_type = flyer_type  
        self.start_x = 700
        self.right_margin = 200
        self.start_y = 1600
        self.bottom_margin = 800
        self.spacing_btw = 50
        self.side_is_vertical = vertical
        self.remove_bg_api_key = remove_bg_api_key



    def remove_bg_from_image(self, img_path):
        """
        This function removes the background of the image by calling the remove.bg API.
        
        Args:
            img_path (str): Path to the image from which the background should be removed.
        
        Returns:
            PIL.Image: Image with the background removed.
        """
        with open(img_path, 'rb') as f:
            r = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                headers={"X-Api-Key": self.remove_bg_api_key},
                files={"image_file": f},
                data={"size": "auto"},
                timeout=60
            )
            
            if r.status_code == requests.codes.ok:
                # Return the image after removing the background
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                return img
            else:
                print("Error:", r.status_code, r.text)
                return None
            
    def process_and_remove_bg(self, img_path):
        """
        Process an image (excluding flyer background) and remove its background.
        
        Args:
            img_path (str): Path to the image to process.
        
        Returns:
            PIL.Image: Processed image with the background removed.
        """
        if img_path != self.background.filename:  # Avoid removing the background of the flyer itself
            return self.remove_bg_from_image(img_path)
        return Image.open(img_path)


    def draw_wrapped_text(self, text, font_name, font_size, font_fill, box_width, box_height=400, line_spacing=0, center=True):
        
        """
        Draws wrapped text inside a defined box width on a given image.

        Args:
            text (str): The text to render.
            position (tuple): (x, y) top-left corner where text starts.
            box_width (int): Maximum width of the text box.
            font_size (int): Font size for text rendering.
            font_path (str): Path to the .ttf font file.
            fill (str/tuple): Text color.
            line_spacing (int): Extra spacing between lines.
        """

        font = ImageFont.truetype(font_name, font_size)

        # --- STEP 1: Prepare temporary image for measuring ---
        temp_img = Image.new("RGBA", (box_width, 1000))  # big temp height
        draw = ImageDraw.Draw(temp_img)

        # ---------- WORD WRAPPING (your same code) -------------
        words = text.split()
        lines = []
        line = ""

        for word in words:
            test_line = line + " " + word if line else word
            line_width = draw.textlength(test_line, font=font)

            if line_width <= box_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = word

        if line:
            lines.append(line)
        # ---------------------------------------------------------

        # --- STEP 2: Measure total needed height ---
        total_height = 0
        for line in lines:
            _, _, _, h = font.getbbox(line)
            total_height += h + line_spacing

        total_height = total_height - line_spacing   # remove last extra spacing

        # If user passed a box_height smaller than needed, overwrite it
        box_height = max(total_height, 1)

        # --- STEP 3: Create final image using dynamic height ---
        inner_img = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(inner_img)

        # --- STEP 4: Draw text normally (your same logic) ---
        y = 0
        for line in lines:
            line_width = draw.textlength(line, font=font)
            x = (box_width - line_width) // 2 if center else 0
            draw.text((x, y), line, font=font, fill=font_fill)
            _, _, _, h = font.getbbox(line)
            y += h + line_spacing

        return inner_img, len(lines)



    def create_title(self, title):

        # box_height = 550
        # Create text image
        header, _ = self.draw_wrapped_text(
            text=title,
            box_width=2500,
            font_size=self.title_font_size,
            font_name=self.title_font,
            font_fill = self.title_font_fill,
            center=False
        ) 

        # Convert to RGBA so we can paste transparently
        header = header.convert("RGBA")

        # Paste the title onto the background
        self.background.paste(header, (800, 800), header)

        self.title_height = header.height

    
    def create_subtitle(self, subtitle, subtitle_description):

        # FONT OBJECTS
        font_big = ImageFont.truetype(self.subheader_font, self.subheader_font_size)
        font_small = ImageFont.truetype(self.subheader_desc_font, self.subheader_desc_font_size)

        # ASCENT DIFFERENCE FOR BASELINE ALIGNMENT
        ascent_big, _ = font_big.getmetrics()
        ascent_small, _ = font_small.getmetrics()
        baseline_offset = ascent_big - ascent_small

        # --- LEFT SUBHEADER ---
        subheader_img, subheader_lines = self.draw_wrapped_text(
            text=subtitle,
            box_width=600,
            box_height=200,
            font_size=self.subheader_font_size,
            font_name=self.subheader_font,
            font_fill=self.subheader_font_fill,
            center=False
        ) # text, font_name, font_size, font_fill, box_width
        subheader_img = subheader_img.convert("RGBA")

        # Subheader top Y
        subheader_y = 800 + self.title_height + 60

        # Paste LEFT text
        self.background.paste(subheader_img, (800, subheader_y), subheader_img)

        # --- RIGHT DESCRIPTION ---
        desc_img, desc_lines = self.draw_wrapped_text(
            text=subtitle_description,
            box_width=2000,
            box_height=200,
            font_size=self.subheader_desc_font_size,
            font_name=self.subheader_desc_font,
            font_fill = self.subheader_desc_font_fill,
            center=False
        )
        desc_img = desc_img.convert("RGBA")

        # Default Y = align to TOP
        desc_y = subheader_y

        # If description is one line → align baseline
        if desc_lines == 1:
            desc_y = subheader_y + baseline_offset

        # Paste RIGHT text
        self.background.paste(
            desc_img,
            (800 + subheader_img.width + 20, desc_y),
            desc_img
        )


    def create_body(self, column):
        if self.flyer_type == "laptop":
            self.create_laptop_body(column)
        else:
            self.create_phone_body(column)


    def scale_image_up(self, img, target_width, target_height):
        """
        Scale an image up to fit within target_width and target_height
        while preserving aspect ratio. Does not shrink images smaller than target.
        
        Args:
            img (PIL.Image): Image to scale.
            target_width (int): Maximum width to scale to.
            target_height (int): Maximum height to scale to.
        
        Returns:
            PIL.Image: Scaled image.
        """
        # Current size
        w, h = img.size

        # Compute scale factor to enlarge proportionally
        scale_w = target_width / w
        scale_h = target_height / h

        # Use the smaller scale to fit within the target box
        scale_factor = min(scale_w, scale_h)

        # Only scale up (ignore if image is already bigger than target)
        if scale_factor > 1:
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        return img
    

    def fit_body(self, body_img_name, face=None, part=None):
        # Process body image to remove its background
        bd_img = Image.open(body_img_name)       
        bbox = bd_img.getbbox()
        bd_img = bd_img.crop(bbox)
        # max_size = (1900, 1900)
        # bd_img = ImageOps.contain(bd_img, max_size)
        
        if (part == "main") and (face == 'front'):
            self.body_imgs.setdefault('main_front', []).append(bd_img) 
        elif (part == "main") and (face == 'back'):
            self.body_imgs.setdefault('main_back', []).append(bd_img) 
        else:
            self.body_imgs.setdefault('other', []).append(bd_img) 



    def create_phone_body(self, columns):
        """Phone flyer body. Supports full-width mode and 2-column layout."""

        image_body = self.body_imgs

        back_imgs = image_body.get('main_back', [])
        front_imgs = image_body.get('main_front', [])
        other_imgs = image_body.get('other', [])

      
        # BASE DIMENSIONS
        total_width = self.background.width - (self.start_x + self.right_margin)
        use_height = self.background.height - (self.start_y + self.bottom_margin)

        
        # COLUMN LOGIC
        if columns:
            left_width = 2 * total_width // 3
           
        else:
            left_width = total_width
          


        # Scale images proportionally
        scaled_imgs_front = []
        scaled_imgs_back = []
        total_img_width = 0
        max_img_height = 0
        for img in front_imgs:
            img_scaled = self.scale_image_up(img, left_width // max(1, len(front_imgs)), use_height)
            scaled_imgs_front.append(img_scaled)
            total_img_width += img_scaled.width
            max_img_height = max(max_img_height, img_scaled.height)

        for img in back_imgs:
            img_scaled = self.scale_image_up(img, left_width // max(1, len(back_imgs)), use_height)
            scaled_imgs_back.append(img_scaled)
            total_img_width += img_scaled.width//2
            max_img_height = max(max_img_height, img_scaled.height)


        # Create composite canvas just big enough for images
        composite_main = Image.new("RGBA", (total_img_width, max_img_height), (0, 0, 0, 0))


        # Paste images horizontally
        past_dist = 0
        for img in scaled_imgs_back:
            composite_main.paste(img, (past_dist, 0), img)
            past_dist += img.width//2
        
        
        for img in scaled_imgs_front:
            composite_main.paste(img, (past_dist, 0), img)
            past_dist += img.width

        
        # Horizontal centering
        if columns:
            x_center = self.start_x + (left_width - composite_main.width) // 2
        else:
            x_center = (self.background.width - composite_main.width) // 2

        # Vertical centering
        y_center = self.start_y + max(0, (use_height - composite_main.height) // 2)

        self.background.paste(composite_main, (x_center, y_center), composite_main)

        # Handle side images
        if columns:
            right_x = self.start_x + left_width
            fake_main = Image.new("RGBA", (0, composite_main.height), (0, 0, 0, 0))
            self.create_side_images(other_imgs, right_x, self.start_y, fake_main)


    def create_laptop_body(self, columns):
        """Laptop flyer body with proper vertical centering."""
        image_body = self.body_imgs
        front_imgs = image_body.get('main_front', [])
        other_imgs = image_body.get('other', [])

        # start_x = 700
        # right_margin = 200
        total_width = self.background.width - self.start_x -self.right_margin

        # start_y = 1700
        # bottom_margin = 750
        use_height = self.background.height - self.start_y - self.bottom_margin

        # Column logic
        left_width = 2 * total_width // 3 if columns else total_width

        # Scale images proportionally
        scaled_imgs = []
        total_img_width = 0
        max_img_height = 0
        for img in front_imgs:
            img_scaled = self.scale_image_up(img, left_width // max(1, len(front_imgs)), use_height)
            scaled_imgs.append(img_scaled)
            total_img_width += img_scaled.width
            max_img_height = max(max_img_height, img_scaled.height)

        # Create composite canvas just big enough for images
        composite_main = Image.new("RGBA", (total_img_width, max_img_height), (0, 0, 0, 0))

        # Paste images horizontally
        past_dist = 0
        for img in scaled_imgs:
            composite_main.paste(img, (past_dist, 0), img)
            past_dist += img.width

        # Horizontal centering
        if columns:
            x_center = self.start_x + (left_width - composite_main.width) // 2
        else:
            x_center = (self.background.width - composite_main.width) // 2

        # Vertical centering
        y_center = self.start_y + max(0, (use_height - composite_main.height) // 2)

        self.background.paste(composite_main, (x_center, y_center), composite_main)

        # Handle side images
        if columns:
            right_x = self.start_x + left_width
            fake_main = Image.new("RGBA", (0, composite_main.height), (0, 0, 0, 0))
            self.create_side_images(other_imgs, right_x, self.start_y, fake_main)
          

    def create_side_images(self, other_imgs, right_x, start_y, composite_main):
        """
        Handle the optional side/extra images, ensuring proper alignment, resizing,
        and vertical centering inside the remaining space to the right of the main body.
        """

       
        # 1) Compute remaining horizontal region (to the right of main)
        remaining_start = right_x + composite_main.width + self.spacing_btw
        remaining_end = self.background.width - self.right_margin
        remaining_width = max(0, remaining_end - remaining_start)

        # 2) Compute usable vertical region
        usable_top = start_y
        usable_bottom = self.background.height - self.bottom_margin
        usable_height = max(0, usable_bottom - usable_top)

        # 3) Determine composite height for side images (vertical stack)
        num_imgs = len(other_imgs)
        if num_imgs == 0:
            return  # nothing to do

        # Compute total height with spacing
        # spacing_between_imgs = 200
        total_img_height = 0
        scaled_imgs = []

        adj_dist = self.spacing_btw * len(other_imgs)+100

        for img in other_imgs:
            if self.side_is_vertical:
                img = self.scale_image_up(img, (remaining_width-adj_dist), (usable_height-adj_dist)//max(1, len(other_imgs)))
            else:
                img = self.scale_image_up(img, ((remaining_width-adj_dist)//max(1, len(other_imgs))), (usable_height-adj_dist))
            scaled_imgs.append(img)
            total_img_height += img.height + self.spacing_btw

        # total_img_height -= spacing_between_imgs  # remove last extra spacing

        # 4) Create composite canvas for side images
        if self.side_is_vertical:
            composite_side = Image.new("RGBA", (min(max(img.width for img in scaled_imgs), remaining_width), total_img_height), (0,0,0,0))

            y_offset = 0
            for img in scaled_imgs:
                x_offset = (composite_side.width - img.width) // 2  # center horizontally
                composite_side.paste(img, (x_offset, y_offset), img)
                y_offset += img.height + self.spacing_btw

        else:
            composite_side = Image.new("RGBA", (remaining_width, min(max(img.height for img in scaled_imgs), total_img_height)), (0,0,0,0))

            x_offset = 0
            for img in scaled_imgs:
                y_offset = (composite_side.height - img.height) // 2  # center horizontally
                composite_side.paste(img, (x_offset, y_offset), img)
                x_offset += img.width + self.spacing_btw

    
        # 6) Compute final x, y positions to center inside remaining space
        x_side = remaining_start + max(0, (remaining_width - composite_side.width) // 2)

        # vertical centering inside usable_height
        if composite_side.height <= usable_height:
            y_side = usable_top + (usable_height - composite_side.height) // 2
        else:
            y_side = usable_top  # too tall → align top to avoid overflow

        # 7) Paste side images on background
        self.background.paste(composite_side, (int(x_side), int(y_side)), composite_side)

        

        
    # def show_image(self):
    #     display(self.background)



    def fit_footer(self, footer_img_name, text):
        ft_img = Image.open(footer_img_name)
        bbox = ft_img.getbbox()
        ft_img = ft_img.crop(bbox)
        max_size = (150, 150)
        ft_img = ImageOps.contain(ft_img, max_size)
        icon_name = footer_img_name.split(".")[-2].split("\\")[-1]
        img_text, _ = self.draw_wrapped_text(text, font_name=self.body_font, font_size=self.body_font_size, font_fill=self.body_font_fill, box_width=430) # text, font_name, font_size, font_fill, box_width

        self.footer_img_list[icon_name] = [ft_img, img_text]





    def create_footer(self):
        image_list = self.footer_img_list.values()

        size = sum([img[0].width + img[1].width for img in image_list]) + 85 * (len(image_list))

        
        footer_height = max(
            max(img[0].height, img[1].height)
            for img in image_list
        ) + 20


        composite = Image.new("RGBA", (size, footer_height), (0,0,0,0)) 

        past_dist = 0

        for icons in image_list:
            for icon in icons:
                composite.paste(icon, (past_dist,0))
                past_dist += icon.width + 20
            
            past_dist += 50
        
        x = (self.background.width - composite.width) //2
        y = self.background.height - 700

        self.background.paste(composite, (x, y), composite)


    
    def fix_logo(self, logo_path):
        logo_img = Image.open(logo_path)
        logo_img = logo_img.convert("RGBA")
        bbox = logo_img.getbbox()
        logo_img = logo_img.crop(bbox)
        max_size = (150, 150)
        logo_img = ImageOps.contain(logo_img, max_size)

        self.background.paste(logo_img, (800, 600), logo_img)




    

