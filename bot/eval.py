# eval.py

import ast
import operator as op
from telegram import Update
from telegram.ext import ContextTypes
import re
# adding operators
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}

def safe_eval(expr: str):
    node = ast.parse(expr, mode='eval').body
    return _eval(node)

def _eval(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](_eval(node.left), _eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](_eval(node.operand))

async def handle_eval_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if re.fullmatch(r'[0-9+\-*/(). ]+', text):  
        result = safe_eval(text)
        formatted_text = f"<b>{text}</b> = <code>{result}</code>"
        await update.message.reply_text(formatted_text, parse_mode="HTML")