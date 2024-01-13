from flask import Flask, render_template
import os
import json
import pandas as pd
app = Flask(__name__)


def getRegionsIso():
    with open(f"{os.getcwd()}/regions_ISO.json", "r", encoding="utf-8") as f:
        regions = json.load(f)
        regions_iso = []
        for region in regions:
            for r in region:
                for i in region[f"{r}"]:
                    regions_iso.append(i)
        return regions_iso


def getPlayedRatesScatters(legends):
    legends_names = []
    legends_img_urls = []
    play_rates = []
    legends_titles = []
    with open(f"{os.getcwd()}/legends/champions_images.json", "r", encoding="utf-8") as f:
        images = json.load(f)
        for legend in legends:
            legend_name = legend["Name"]
            if legend_name.find("'") != -1:
                legend_name = legend_name.replace("'", "")
            if legend_name.find(" ") != -1:
                legend_name = legend_name.replace(" ", "")
            if legend_name.find(".") != -1:
                legend_name = legend_name.replace(".", "")
            if legend_name.find("&") != -1:
                legend_name = legend_name.split("&")[0]
            legend_name = legend_name.upper()
            legends_names.append(legend_name)
            legends_titles.append(legend["Title"])
            if legend_name == "AKSHAN":
                url = images["ASKHAN"]
                legends_img_urls.append(
                    url
                )
            elif legend_name == "BRIAR":
                url = images["BRIAR"]
                legends_img_urls.append(
                    url
                )
            elif legend_name == "RELL":
                url = images["RELL"]
                legends_img_urls.append(
                    url
                )
            else:
                legends_img_urls.append(
                    images[legend_name]
                )
            play_rates.append(legend["General Played Rate"])
    pd_legends_names = pd.Series(legends_names)
    pd_legends_img_urls = pd.Series(legends_img_urls)
    pd_play_rates = pd.Series(play_rates)
    pd_legends_titles = pd.Series(legends_titles)
    datalist = [pd_legends_names, pd_legends_img_urls,
                pd_play_rates, pd_legends_titles]
    return datalist


def getTags(legends):
    pri_tags = {}
    tags = {}
    for legend in legends:
        tag = ""
        for p_tag in legend["Tags"]:
            if list(pri_tags.keys()).__contains__(p_tag):
                pri_tags[p_tag] = pri_tags[p_tag] + 1
            else:
                pri_tags[p_tag] = 1
            tag = tag + " " + p_tag
        if list(tags.keys()).__contains__(tag):
            tags[tag] = tags[tag] + 1
        else:
            tags[tag] = 1
    pd_pri_tags = pd.Series(list(pri_tags.keys()))
    pd_pri_counts = pd.Series(list(pri_tags.values()))
    pd_tags = pd.Series(list(tags.keys()))
    pd_counts = pd.Series(list(tags.values()))
    return [pd_pri_tags, pd_pri_counts, pd_tags, pd_counts]


def getPositionBasedData(legends):
    data = {
        "Top": [],
        "Jungle": [],
        "Middle": [],
        "Bottom": [],
        "Utility": []
    }
    for legend in legends:
        for position in legend["Positions"][0]:
            if legend["Positions"][0][position] != 0:
                data[position].append({
                    "Name": legend["Name"],
                    "Rate": legend["Positions"][0][position],
                    "Tags": legend["Tags"],
                    "Title": legend["Title"],
                    "Attack": legend["Info"][0]["Attack"],
                    "Defense": legend["Info"][0]["Defense"],
                    "Difficulty": legend["Info"][0]["Difficulty"],
                    "Magic": legend["Info"][0]["Magic"]
                })
    return data
# barchart fonksiyonu


def getChampsRoleInfo(champions_data):
    primary_role_f = {}
    primary_role_m = {}
    primary_role_o = {}

    lane_f = {}
    lane_m = {}
    lane_o = {}

    for champion in champions_data:
        gender = champion.get("Gender", "Other").lower()
        primary_role = champion.get("Primary Role", "Unknown")
        lane = champion.get("Lane", "Unknown")

        if primary_role not in primary_role_f:
            primary_role_f[primary_role] = 0
        if primary_role not in primary_role_m:
            primary_role_m[primary_role] = 0
        if primary_role not in primary_role_o:
            primary_role_o[primary_role] = 0

        if gender == "female":
            primary_role_f[primary_role] += 1
        elif gender == "male":
            primary_role_m[primary_role] += 1
        else:
            primary_role_o[primary_role] += 1

        if lane not in lane_f:
            lane_f[lane] = 0
        if lane not in lane_m:
            lane_m[lane] = 0
        if lane not in lane_o:
            lane_o[lane] = 0

        if gender == "female":
            lane_f[lane] += 1
        elif gender == "male":
            lane_m[lane] += 1
        else:
            lane_o[lane] += 1

    # Pandas Series nesnelerine çevirme
    pd_primary_role_female = pd.Series(primary_role_f, name="Female")
    pd_primary_role_male = pd.Series(primary_role_m, name="Male")
    pd_primary_role_other = pd.Series(primary_role_o, name="Other")

    pd_lane_female = pd.Series(lane_f, name="Female")
    pd_lane_male = pd.Series(lane_m, name="Male")
    pd_lane_other = pd.Series(lane_o, name="Other")

    return pd_primary_role_female, pd_primary_role_male, pd_primary_role_other, pd_lane_female, pd_lane_male, pd_lane_other


# piechart fonksiyonu
def getGender(champion_data):
    gender_f = {}
    gender_m = {}
    gender_o = []

    for champion in champion_data:
        if "Gender" in champion:
            gender = champion["Gender"].lower()
            champion_info = {
                "Champion Name": champion["Champion Name"], "Gender": champion["Gender"]}

            if gender == "female":
                if gender not in gender_f:
                    gender_f[gender] = [champion_info]
                else:
                    gender_f[gender].append(champion_info)
            elif gender == "male":
                if gender not in gender_m:
                    gender_m[gender] = [champion_info]
                else:
                    gender_m[gender].append(champion_info)
            else:
                gender_o.append(champion_info)

    female_count = sum(len(champions) for champions in gender_f.values())
    male_count = sum(len(champions) for champions in gender_m.values())
    other_count = len(gender_o)

    # Pandas Series oluşturma
    pd_gender_f = pd.Series(gender_f)
    pd_gender_m = pd.Series(gender_m)
    pd_gender_o = pd.Series(gender_o)

    return female_count, male_count, other_count, pd_gender_f, pd_gender_m, pd_gender_o


@app.route('/')
def main():
    with open(f"{os.getcwd()}/legends/legends.json", "r", encoding="utf-8") as f:
        legends = json.load(f)
    with open(f"{os.getcwd()}/legends/champions_attributes.json", "r", encoding="utf-8") as f:
        champions_gender = json.load(f)

    # Verileri kullanarak fonksiyonu çağırma
    female_count, male_count, other_count, pd_gender_f, pd_gender_m, pd_gender_o = getGender(
        champions_gender)
    pd_primary_role_female, pd_primary_role_male, pd_primary_role_other, pd_lane_female, pd_lane_male, pd_lane_other = getChampsRoleInfo(
        champions_gender)
    datalist_scatter = getPlayedRatesScatters(legends)
    tagslist_pie_chart = getTags(legends)
    position_based_datas = getPositionBasedData(legends)
    with open(f"{os.getcwd()}/legends/champions_images.json", "r", encoding="utf-8") as f:
        images = json.load(f)
    for legend in legends:
        legend_name = legend["Name"]
        if legend_name.find("'") != -1:
            legend_name = legend_name.replace("'", "")
        if legend_name.find(" ") != -1:
            legend_name = legend_name.replace(" ", "")
        if legend_name.find(".") != -1:
            legend_name = legend_name.replace(".", "")
        if legend_name.find("&") != -1:
            legend_name = legend_name.split("&")[0]
        legend["Name"] = legend_name.upper()
    return render_template("index.html",
                           mpcn=datalist_scatter[0].to_list(),
                           mpci=datalist_scatter[1].to_list(),
                           mpcr=datalist_scatter[2].to_list(),
                           mpct=datalist_scatter[3].to_list(),
                           pri_tags=tagslist_pie_chart[0].to_list(),
                           pri_counts=tagslist_pie_chart[1].to_list(),
                           tags=tagslist_pie_chart[2].to_list(),
                           counts=tagslist_pie_chart[3].to_list(),
                           p_based_datas=position_based_datas,
                           legends=legends,
                           images=images,
                           female_count=female_count,
                           male_count=male_count,
                           other_count=other_count,
                           pd_gender_f=pd_gender_f,
                           pd_gender_m=pd_gender_m,
                           pd_gender_o=pd_gender_o,
                           pd_primary_role_female=pd_primary_role_female,
                           pd_primary_role_male=pd_primary_role_male,
                           pd_primary_role_other=pd_primary_role_other,
                           pd_lane_female=pd_lane_female,
                           pd_lane_male=pd_lane_male,
                           pd_lane_other=pd_lane_other
                           )


if __name__ == "__main__":
    app.run()
