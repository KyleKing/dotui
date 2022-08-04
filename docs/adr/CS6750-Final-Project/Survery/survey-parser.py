"""Parse the Survey Results for M5

pipx install watchfiles
watchfiles "poetry run python survey-parser.py" ./survey-parser.py

"""

import re
import json
from collections import defaultdict
from operator import indexOf
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger
from wordcloud import WordCloud

RE_PUNCTUATION = re.compile(r"[\.,'\":] ")
pd.options.plotting.backend = "plotly"

# lookup (Survey 1)
# {'1658830447755': 'Which software application(s) do you currently use to for managing "dotfiles"?',
#  '1658830487054': 'What convinced you start managing dotfiles?',
#  '1658830495831': 'What is your favorite feature of your preferred dotfile management application (or why did you select it over others)?',
#  '1658830503468': 'What challenges do you face when managing dotfiles (or what made it difficult to start)?',
#  '1658830509922': "If you have used yadm, what do you like or dislike about the tool? (Optionally, if you haven't used yadm, but want to skim the README, feel free to leave feedback here as well)",
#  '1658830512656': 'Which method(s) do you use for tracking changes and/or syncing?',
#  '1658830514751': 'If you selected Other, describe what you use here:',
#  '1658830516586': 'If you track changes, what do you use to stage changes and resolve conflicts?',
#  '1658830518073': 'What operating systems do you currently have dotfiles installed on?',
#  '1658830584480': 'On how many computers (virtual or physical) do you currently have your dotfiles?',
#  '1658830585934': 'If you sync dotfiles between computers, how do you manage configuration differences between machines?',
#  '1658830587546': 'How do you identify what dotfiles should be managed?',
#  '1658830637839': 'How frequently do you use a terminal, such Windows Command Prompt or Mac Terminal?',
#  '1658830705400': 'Have you installed dotfiles from another user for work or personal computer? If so, what did you like or dislike about that process?',
#  '1658830706687': 'Do you share snippets intended for dotfiles or computer configuration at work? If so, are they shared manually or do you have a tool? Are they in version control and/or synced '
#                   'automatically? Roughly how many people are involved?',
#  '1658830707987': "If you answered the above question, what works or doesn't work about the current way configuration is shared?",
#  '1658830709187': 'What is your job title or professional role?',
#  '1658830723736': 'Thank you for completing this survey! Please leave any general comments about managing dotfiles or this survey here.',
#  '1658983549206': 'If you selected “Other” or “Custom Scripts,” can you elaborate on what tools you use?'}

# lookup (Survey 2)
# {'1659105327355': 'As an open-ended question, what change(s) would you make to yadm?',
#  '1659105366133': 'What features would help interacting with git/syncing for yadm?',
#  '1659105400230': 'Could you explain more about how those changes might better meet your needs?',
#  '1659105415802': 'As a check that you know yadm, what is one library that can be used for encryption and decryption?',
#  '1659105681017': 'If you selected Other(s), what are those?',
#  '1659112212277': 'Where could yadm make managing dotfiles easier?'}

# ids (Survey 1)
ID_01_MS_CURRENT_MANAGE_TOOLS = "1658830447755"
ID_02_TXT_CURRENT_OTHER_TOOLS = "1658983549206"
ID_03_TXT_CONVINCED_TO_START = "1658830487054"
ID_04_TXT_FAVORITE_FEATURE = "1658830495831"
ID_05_TXT_CHALLENGES = "1658830503468"
ID_06_TXT_YADM_OPINIONS = "1658830509922"
ID_07_MS_CURRENT_SYNC_TOOLS = "1658830512656"
ID_08_TXT_CURRENT_SYNC_TOOLS_OTHER = "1658830514751"
ID_09_TXT_DIFF_TOOL = "1658830516586"
ID_10_MS_CURRENT_OSES = "1658830518073"
ID_11_SEL_COUNT_SYNC_COMPUTERS = "1658830584480"
ID_12_TXT_MANAGE_OS_SPECIFIC = "1658830585934"
ID_13_TXT_IDENTIFY_FILES_FOR_MANAGEMENT = "1658830587546"
ID_14_SEL_TERMINAL_USE_FREQUENCY = "1658830637839"
ID_15_TXT_USING_ANOTHERS_DOTFILES = "1658830705400"
ID_16_TXT_SHARED_WORK_DOTFILES = "1658830706687"
ID_17_TXT_WHAT_WORKS_WHEN_SHARING = "1658830707987"
ID_18_TXT_JOB_TITLE = "1658830709187"
ID_19_TXT_GENERAL_COMMENTS = "1658830723736"

# ids (Survey 2)
ID_1_TXT_CHANGES_TO_YADM = "1659105327355"
ID_2_MS_NEW_SYNC_FEAT = "1659105366133"
ID_3_MS_NEW_GENERAL_FEAT = "1659112212277"
ID_4_TXT_OTHERS = "1659105681017"
ID_5_TXT_EPLAINATION = "1659105400230"
ID_6_TXT_TRANSCRYPT_CHECK = "1659105415802"

SURVEY_2_KEYS = [
    # ID_1_TXT_CHANGES_TO_YADM
    "Better description of what changes to the diff would do to local files",  # 2
    "Better descriptions over which diff is local vs. remote when pulling upstream changes",  # 1
    "Better integration with Git applications, such as Gitkrakken, Github Desktop, etc.",  # 1
    "Better listing of which files are currently managed by yadm",  # 2
    "Difficulty with determining how to use the git CLI commands from yadm (addressed with better documentation, help, etc.)",
    "Easier conflict resolution if local changes conflict with upstream",  # 1
    "Easier way to undo changes after a mistake",
    # "Other(s)",
    # "None",
    # ID_3_MS_NEW_GENERAL_FEAT
    "Better way to discover code snippets that may be useful",  # 1
    "Built-in formatter or linter that keeps code consistent and can catch syntax errors on commit",
    "Built-in identification of possible secrets in code before allowing a commit",  # 1
    "Composability to sync partial snippets from coworkers and peers without syncing all of them",  # 1
    "Discovery of which configuration files in your local environment are good to track, like which files from VSCode should be synced (and which shouldn't)",
    "Easier setup of new computers",  # 1
    "Easier to make dotfiles operating-system specific",
    "Easier way to edit templates where environment variables are used",
    "Easier way to regenerate templates when you want to change a variable",  # 1
    "If syncing with multiple computers, easier ways to commit changes and share",
    "If using a single computer, automatic syncing and backup",
    "Notification of new changes in upstream that should be synced",  # 1
    "Other(s)",
    "None",
]


def collect_results(raw_results) -> tuple[dict[str, str], dict[str, str], pd.DataFrame]:
    lookup_dict: dict[str, str] = dict(
        [(result["id"], result["text"]) for result in raw_results]
    )
    question_lookup: dict[str, str] = dict(
        [(result["id"], result["text"]) for result in raw_results]
    )
    results: dict[str, list] = {
        result["id"]: result["answers"] for result in raw_results
    }

    df_results = pd.DataFrame.from_dict(
        {lookup_dict[key]: value for key, value in results.items()}
    )

    return lookup_dict, question_lookup, df_results


def make_fig_dir() -> Path:
    base_dir = "../Figures"
    figure_dir = Path(base_dir)
    figure_dir.mkdir(exist_ok=True)
    return figure_dir


def plot_counts(
    lookup_dict: dict[str, str], question_lookup: dict[str, str], df_data: pd.DataFrame
) -> None:
    figure_dir = make_fig_dir()

    demographic_columns = [
        (ID_01_MS_CURRENT_MANAGE_TOOLS, "Tools for Management"),
        (ID_07_MS_CURRENT_SYNC_TOOLS, "Tools for Syncing"),
        (ID_10_MS_CURRENT_OSES, "Operating Systems"),
        (ID_11_SEL_COUNT_SYNC_COMPUTERS, "Count of Computers"),
        (ID_14_SEL_TERMINAL_USE_FREQUENCY, "Terminal Use Frequency"),
    ]
    for d_id, d_text in demographic_columns:
        df_plot = df_data[[lookup_dict[d_id]]]
        df_plot.columns = [d_text]
        fig = df_plot.plot.bar(
            barmode="group",
            template="simple_white",
            title=question_lookup[d_id],
        )
        fig.update_layout(showlegend=False)
        fig.write_image((figure_dir / f"bar-{d_text}.png".replace(" ", "-")))


def plot_wordcharts(lookup_dict: dict[str, str], df_data: pd.DataFrame) -> None:
    figure_dir = make_fig_dir()

    text_col_ids = [
        # > (ID_02_TXT_CURRENT_OTHER_TOOLS, "CURRENT_OTHER_TOOLS"),
        (ID_03_TXT_CONVINCED_TO_START, "CONVINCED_TO_START"),
        (ID_04_TXT_FAVORITE_FEATURE, "FAVORITE_FEATURE"),
        (ID_05_TXT_CHALLENGES, "CHALLENGES"),
        (ID_06_TXT_YADM_OPINIONS, "YADM_OPINIONS"),
        # > (ID_08_TXT_CURRENT_SYNC_TOOLS_OTHER, "CURRENT_SYNC_TOOLS_OTHER"),
        (ID_09_TXT_DIFF_TOOL, "DIFF_TOOL"),
        (ID_12_TXT_MANAGE_OS_SPECIFIC, "MANAGE_OS_SPECIFIC"),
        (ID_13_TXT_IDENTIFY_FILES_FOR_MANAGEMENT, "IDENTIFY_FILES_FOR_MANAGEMENT"),
        (ID_15_TXT_USING_ANOTHERS_DOTFILES, "USING_ANOTHERS_DOTFILES"),
        (ID_16_TXT_SHARED_WORK_DOTFILES, "SHARED_WORK_DOTFILES"),
        (ID_17_TXT_WHAT_WORKS_WHEN_SHARING, "WHAT_WORKS_WHEN_SHARING"),
        # > (ID_18_TXT_JOB_TITLE, "JOB_TITLE"),  # Not useful
        # > (ID_19_TXT_GENERAL_COMMENTS, "GENERAL_COMMENTS"),  # Not useful
    ]
    filtered_tokens = set(
        ("dotfile dotfiles file files yes sure nope n/a na via").split(" ")
    )

    all_text = ""
    for col_id, short_label in text_col_ids:
        key = lookup_dict[col_id]
        raw_text = (
            " ".join(df_data[key].to_list())
            .lower()
            .rstrip(".")
            .replace("e.g.", "")
            .replace("i.e.", "")
        )
        tokens = RE_PUNCTUATION.sub(" ", raw_text).split(" ")
        text = " ".join(
            token for token in tokens if token and token not in filtered_tokens
        )
        all_text += "\n" + text

        wordcloud = WordCloud(background_color="white").generate(text)
        plt.imshow(wordcloud, interpolation="bilinear")
        title = key if len(key) < 55 else key[:55] + "..."
        plt.title(title)
        plt.axis("off")
        plt.savefig(
            (figure_dir / f"wordcloud-{short_label}.png".replace(" ", "-")).as_posix(),
            bbox_inches="tight",
            pad_inches=0,
        )
        plt.close()

    wordcloud = WordCloud(background_color="white", max_font_size=55).generate(all_text)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title("Overall Short Answer Questions Word Cloud")
    plt.axis("off")
    plt.savefig(
        (figure_dir / "wordcloud.png").as_posix(),
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close()


def split_multi(
    lookup_dict: dict[str, str],
    df_data: pd.DataFrame,
    ids: list[str],
    title: str,
    short_name: str,
    all_options: list[str],
) -> None:
    figure_dir = make_fig_dir()

    total = df_data.shape[0]
    data = {key: 0 for key in all_options} if all_options else defaultdict(lambda: 0)
    for _id in ids:
        for resp in df_data[lookup_dict[_id]].to_list():
            for key in resp.split(";"):
                data[key] += 1

    df_plot = pd.DataFrame.from_dict(
        {
            key[:45]: [value]
            for key, value in sorted(data.items(), key=lambda x: x[1], reverse=True)
        }
    )
    df_plot = df_plot.T
    df_plot.columns = [f"Out of {total}"]
    fig = df_plot.plot.bar(
        barmode="relative",
        template="simple_white",
        title=title,
    )
    fig.update_layout(legend_title_text=short_name)
    fig.write_image((figure_dir / f"multi-select-{short_name}.png".replace(" ", "-")))


if __name__ == "__main__":
    path_results_1 = Path(__file__).parent / "survey_results.json"
    path_results_2 = Path(__file__).parent / "survey_2_results.json"

    lookup_results_1, question_lookup_1, df_results_1 = collect_results(
        json.loads(path_results_1.read_text())
    )
    lookup_results_2, question_lookup_2, df_results_2 = collect_results(
        json.loads(path_results_2.read_text())
    )

    plot_counts(lookup_results_1, question_lookup_1, df_results_1)
    plot_wordcharts(lookup_results_1, df_results_1)

    ids_1 = [
        (ID_01_MS_CURRENT_MANAGE_TOOLS, "Tools for Management"),
        (ID_07_MS_CURRENT_SYNC_TOOLS, "Tools for Syncing"),
        (ID_10_MS_CURRENT_OSES, "Operating Systems"),
    ]
    for _id, short_name in ids_1:
        title = question_lookup_1[_id]
        split_multi(lookup_results_1, df_results_1, [_id], title, short_name, [])

    ids_2 = [ID_2_MS_NEW_SYNC_FEAT, ID_3_MS_NEW_GENERAL_FEAT]
    title = "Survey 2 Multi-Select Question Results"
    short_name = title
    split_multi(lookup_results_2, df_results_2, ids_2, title, short_name, SURVEY_2_KEYS)
