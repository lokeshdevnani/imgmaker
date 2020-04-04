from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from jinja2 import Template
import io


class imgmaker:
    def __init__(self, chromedriver_path, scale=2):
        assert isinstance(scale, int), "scale must be an integer."
        self.scale = scale

        chrome_options = Options()

        for arg in [
            "--headless",
            "--hide-scrollbars",
            "--disable-gpu",
            f"--force-device-scale-factor={scale}",
        ]:
            chrome_options.add_argument(arg)

        self.driver = webdriver.Chrome(
            executable_path=chromedriver_path, options=chrome_options
        )

    def generate(
        self,
        template_path,
        template_params,
        width=1024,
        height=None,
        downsample=True,
        output_file="img.png",
    ):
        html = render_html_template(template_path, template_params)
        self.driver.get(f"data:text/html;charset=utf-8,{html}")

        if height is None:
            height = self.driver.find_element_by_tag_name("html").size["height"]
        self.driver.set_window_size(width, height)

        if self.scale > 1 and downsample:
            img = Image.open(io.BytesIO(self.driver.get_screenshot_as_png()))
            img = img.resize(
                (int(img.size[0] / self.scale), int(img.size[1] / self.scale)),
                Image.ANTIALIAS,
            )
            img.save(output_file)
        else:
            self.driver.get_screenshot_as_file(output_file)

    def close(self):
        self.driver.close()


def render_html_template(template_path, template_params):
    with open(template_path) as f:
        html_template = Template(f.read())
    return html_template.render(template_params)


if __name__ == "__main__":
    c = imgmaker("/Users/maxwoolf/Downloads/chromedriver")
    c.generate(
        "test_template.html",
        {
            "title": "I am a pony!",
            "subtitle": "It is true!",
            "color": "success",
            "bold": True,
            "center": True,
        },
        width=800,
        height=450,
    )
    c.close()
