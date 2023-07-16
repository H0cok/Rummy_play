import base64
import random
import unittest
from PIL import Image
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import io
from image_comparison import get_img
from concurrent.futures import ThreadPoolExecutor

capabilities = dict(
    platformName="Android",
    automationName="uiautomator2",
    deviceName="d3e64cf2"
)

appium_server_url = 'http://localhost:4723'


def crop_image(el, fl=False):
    screenshot_base64 = el.screenshot_as_base64

    img_data = base64.b64decode(screenshot_base64)
    img = Image.open(io.BytesIO(img_data))
    thresh = 100
    fn = lambda x: 255 if x > thresh else 0
    img = img.convert('L').point(fn, mode='1')
    # Crop the image
    if fl:
        img = img.transpose(Image.ROTATE_270)

        cropped_img = img.crop((20, 20, 80, 100))
    else:
        cropped_img = img.crop((20, 20, 80, 180))
    # Convert the cropped image to bytes
    cropped_img_byte_arr = io.BytesIO()
    cropped_img.save(cropped_img_byte_arr, format='PNG')
    cropped_img_bytes = cropped_img_byte_arr.getvalue()
    return cropped_img_bytes


class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, capabilities)
        with open("dict_data.pickle", "rb") as card_file:
            self.cards = pickle.load(card_file)

        with open("num_data.pickle", "rb") as card_file:
            self.nums = pickle.load(card_file)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_play_rummy(self) -> None:
        # find all starting card elements
        parent_layout = self.driver.find_element(by=AppiumBy.ID, value='com.eastudios.indianrummy:id/frmUserCards')
        self.image_elements = parent_layout.find_elements(by=AppiumBy.CLASS_NAME, value='android.widget.ImageView')

        # get the joker card
        joker = self.get_joker()

        # gets list of items with full card info using multiple threads
        with ThreadPoolExecutor() as executor:
            hand_cards = list(executor.map(self.get_card_info, range(2, 16)))

        # gets a position of discard pile
        dis_pos = [x for x in hand_cards if x["pos"]["y"] < self.driver.get_window_size()["height"] / 2][0]["pos"]
        dis_pos = (dis_pos["x"], dis_pos["y"])

        # gets the list of cards that we need to complete some group
        needed = self.find_needed_cards(hand_cards, joker)

        # main game loop
        while True:
            try:
                declare_button = self.driver.find_element(by=AppiumBy.ID, value='com.eastudios.indianrummy:id/btnDeclare')
                declare_button.click()
                break
            except NoSuchElementException:
                self.play_move(dis_pos, needed)

    def get_joker(self):
        joker_element = self.image_elements[1]
        joker_img = crop_image(joker_element, True)
        joker_img = get_img(list(self.nums.keys()), joker_img)
        joker = self.nums[joker_img]
        print(f"Joker card: {joker}")
        return joker

    def get_card(self, el):
        card_img = crop_image(el, False)
        card_img = get_img(list(self.cards.keys()), card_img)
        return self.cards[card_img]

    def get_card_info(self, card_num, card=True):
        card_el = self.image_elements[card_num]
        if card:
            return {"card": self.get_card(card_el),
                    "pos": card_el.location,
                    "id": card_el.id}
        else:
            return {"pos": card_el.location,
                    "id": card_num}

    def get_groups(self, hand_cards):
        hand_cards = [x for x in hand_cards if x["pos"]["y"] > self.driver.get_window_size()["height"] / 2]
        hand_cards.sort(key=lambda x: x["pos"]["x"])
        length = min([-x["pos"]["x"] + hand_cards[i + 1]["pos"]["x"] for i, x in enumerate(hand_cards[:-1])])
        groups = []
        tmp = []
        for idx, card in enumerate(hand_cards[:-1]):
            tmp.append(card)
            if hand_cards[idx + 1]["pos"]["x"] - card["pos"]["x"] - 10 > length:
                groups.append(tmp)
                tmp = []
        tmp.append(hand_cards[-1])
        groups.append(tmp)
        return groups

    def find_needed_cards(self, hand_cards, joker):
        card_sequence = ["a"] + [str(i) for i in range(2, 10)] + ["1", "j", "q", "k"]
        needed = []
        groups = self.get_groups(hand_cards)
        for idx_gr, group in enumerate(groups):
            jokers = 0
            cards_n = [x["card"] for x in group]
            if len(group) < 2:
                continue
            while 1:
                for idx, card in enumerate(cards_n):
                    if card[0] == "a" or card[1] == joker:
                        jokers += 1
                        break
                else:
                    break
                cards_n.pop(idx)
            for i in cards_n:
                if i[0] != cards_n[0][0]:

                    for i in cards_n:
                        if i[1] != cards_n[0][1]:
                            break
                    else:
                        needed.extend(set([x + cards_n[0][1] for x in ["s", "g", "b", "h"]]).difference(cards_n))
                    break
            else:
                start = max((0, card_sequence.index(cards_n[0][1]) - jokers - 1))
                fin = min((len(card_sequence), card_sequence.index(cards_n[-1][1]) + jokers + 1))
                new_need = list(set(card_sequence[start:fin]).difference(set([x[1] for x in cards_n])))
                needed.extend([cards_n[0][0] + x for x in new_need])
        return needed

    def play_move(self, dis_pos, needed):
        try:
            # Wait up to 30 seconds for the element to be visible
             WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, "com.eastudios.indianrummy:id/btnDrop")))
        except:
            print("Program is not responding")
            return None

        parent_layout = self.driver.find_element(by=AppiumBy.ID, value='com.eastudios.indianrummy:id/frmUserCards')
        self.image_elements = parent_layout.find_elements(by=AppiumBy.CLASS_NAME, value='android.widget.ImageView')
        for idx, el in enumerate(self.image_elements):
            if dis_pos[0] == el.rect["x"] and dis_pos[1] == el.rect["y"]:
                discard_card = self.get_card(el)
                break
        if discard_card not in needed:
            el = self.driver.find_element(by=AppiumBy.ID, value="com.eastudios.indianrummy:id/ivDackCardBase")
        else:
            needed.pop(needed.index(discard_card))
        el.click()
        hand_cards = []
        for idx in range(2,16):
            hand_cards.append(self.get_card_info(idx, False))
        groups = self.get_groups(hand_cards)
        eliminated_card_id = random.choice(groups[-1])["id"]
        eliminated_card_element = self.image_elements[eliminated_card_id]
        eliminated_card_element.click()
        discard_button = self.driver.find_element(by=AppiumBy.ID, value="com.eastudios.indianrummy:id/btnDiscard")
        discard_button.click()



if __name__ == '__main__':
    unittest.main()
