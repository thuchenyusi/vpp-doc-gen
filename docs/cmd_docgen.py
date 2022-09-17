#!/usr/bin/env python3

from pydoc import cli
import re
from enum import Enum, auto

outpath = r"./cmdline.md"

CLI_FILE_LIST = [r"../cli/ikev2_cli.c",
                 r"../cli/ipsec_cli.c"]


class CmdPart(Enum):
    CLI_PATH = auto()
    CLI_SHORT_HELP = auto()
    CLI_FUNCTION = auto()


CMD_REGEX_MATCH = (
    ("path", r"\.path =([^},]*)"),
    ("shortHelp", r"\.short_help =([^},]*)"),
    ("function", r"\.function =([^},]*)"),
)

REGEX_CMD = (
    r"VLIB_CLI_COMMAND \([^\)]*\) = {"
    r"(?P<cmd>[^}]*)"
    r"};"
)

PARA_TYPE_DICT = {
    "u32": ("32位无符号整型", "[0, 2^32)"),
    "u64": ("64位无符号整型", "[0, 2^64)"),
    "str": ("字符串", ""),
    "enum": ("枚举", "")
}

for cli_filename in CLI_FILE_LIST:
    with open(cli_filename) as clifile:
        for cli_file_line in clifile:
            cli_file_line = cli_file_line.strip()


class CmdPara:
    def __init__(self):
        self.name = "TODO"
        self.meaning = "TODO"
        self.optional = "TODO"
        self.type = "TODO"
        self.range = "TODO"


def enum_to_range(str):
    ret = str
    ret = re.sub(r"<|>|\[|\]", r"", ret)
    ret = re.sub(r"\|", r"、", ret)
    return ret


def short_help_to_para(short_help):
    para_set = set()
    pare_regex = (
        (r"<[^<>\|]*>", "必须", "TODO"),
        (r"\[[^\[\]\|]*\]", "可选", "TODO"),
        (r"<[^<>]*\|[^<>]*>", "必须", "枚举"),
        (r"\[[^\[\]]*\|[^\[\]]*\]", "可选", "枚举")
    )
    for line in short_help.split("\n"):
        for pattern, para_optional, para_type in pare_regex:
            for para in re.findall(pattern, line):
                cmd_para = CmdPara()
                cmd_para.name = para
                cmd_para.optional = para_optional
                cmd_para.type = para_type
                if cmd_para.type == "枚举":
                    cmd_para.range = enum_to_range(para)
                para_set.add(cmd_para)
    return para_set


def str_to_markdown_pre(str):
    ret = str
    ret = re.sub(r"<", r"\<", ret)
    ret = re.sub(r">", r"\>", ret)
    ret = re.sub(r"\]", r"\\]", ret)
    ret = re.sub(r"\[", r"\\[", ret)
    ret = re.sub(r"\|", r"\\|", ret)
    return ret


def cli_command_markdown(cmd):
    md = "## 命令\n\n" + str_to_markdown_pre(cmd.path) + "\n\n"
    return md


def cli_grammar_markdown(cmd):
    md = "## 语法\n\n" + \
        str_to_markdown_pre(cmd.shortHelp.replace("\n", "\n\n")) + "\n\n"
    return md


def cli_para_markdown(cmd):
    if not cmd.para:
        return ""
    md = "## 参数\n\n" + "| 参数名 | 含义 | 可选性 | 类型 | 范围 |\n" + \
        "| --- | --- | --- | --- | --- |\n"
    for para in cmd.para:
        md += "| " + str_to_markdown_pre(para.name) + \
            " | "+str_to_markdown_pre(para.meaning) +\
            " | "+str_to_markdown_pre(para.optional) +\
            " | "+str_to_markdown_pre(para.type) +\
            " | "+str_to_markdown_pre(para.range) + " |\n"
    md += "\n"
    return md


class Cmd:
    def __init__(self):
        self.path = ""
        self.shortHelp = ""
        self.function = ""

    def print(self):
        for attr_name, pattern in CMD_REGEX_MATCH:
            print(attr_name+"\n"+getattr(self, attr_name))

    def set(self, part, content):
        setattr(self, part, content)

    def para_parse(self):
        self.para = short_help_to_para(self.shortHelp)

    def to_markdown(self):
        md = "# " + str_to_markdown_pre(self.path) + "\n\n"
        md += cli_command_markdown(self)
        md += cli_grammar_markdown(self)
        md += cli_para_markdown(self)
        return md


def clean_cmd_attr(cmd_attr):
    cmd_attr = re.sub(r"\"", r"", cmd_attr)
    cmd_attr = re.sub(r"\n", r" ", cmd_attr)
    cmd_attr = re.sub(r"[ ]+", r" ", cmd_attr)
    cmd_attr = re.sub(r"\\n", r"\n", cmd_attr)

    return cmd_attr


def cli_cmd_handle(cli_cmd, cli_cmd_list):
    cmd = Cmd()
    for attr_name, pattern in CMD_REGEX_MATCH:
        cmd_attr = re.search(pattern, cli_cmd, re.MULTILINE).group(1)
        cmd.set(attr_name, clean_cmd_attr(cmd_attr))
        cmd.para_parse()
    cli_cmd_list.append(cmd)
    return


def clifile_handle(clifile, cli_cmd_list):
    for cli_cmd in re.findall(REGEX_CMD, clifile.read(), re.MULTILINE):
        cli_cmd_handle(cli_cmd, cli_cmd_list)
    return


OUT_FILE = "../output/cmdlinehelp.md"

for cli_filename in CLI_FILE_LIST:
    print(cli_filename)
    cli_cmd_list = []
    out_file = open(OUT_FILE, "a")
    out_file.truncate(0)
    with open(cli_filename) as clifile:
        clifile_handle(clifile, cli_cmd_list)
    for cmd in cli_cmd_list:
        out_file.write(cmd.to_markdown())
    out_file.close()
