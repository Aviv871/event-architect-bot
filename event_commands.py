import logging
import hashlib
from typing import Dict, List
from telegram import (
    ReplyKeyboardMarkup,
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from Event import EventData, EventItem
from state import *

global_events: Dict[str, EventData] = {}


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bye! Hope to talk to you again soon.", reply_markup=ReplyKeyboardRemove()
    )
    return END


async def create_or_join_event(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if context.args:
        logging.info("[New Request] Got join event request request")
        event_id = context.args[0]
        if event_id not in global_events:
            logging.warning("Got an unknowen event it: %s", event_id)
            return END
        context.user_data["newest_event_id"] = event_id
        event_data = global_events[event_id]
        event_data.users.add(update.effective_user)
        return await handle_user_joined(update, context)
    else:
        logging.info("[New Request] Got new create event request")
        await update.message.reply_text(
            "Hi! Do you want me to help you orginaize a new event?\n"
            "Let's get some details about the event you're creating.\n"
            "<b>Chose a unique name for your event:</b>",
            parse_mode="HTML",
        )
        return ENTERED_NEW_EVENT_NAME


async def handle_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_event_name = update.message.text.strip()
    if new_event_name in global_events:
        await update.message.reply_text(
            f"The name '{new_event_name}' is alreay taken 🥲\n"
            f"Please enter a new name:\n",
            parse_mode="HTML",
        )
        return ENTERED_NEW_EVENT_NAME

    context.user_data["newest_event_id"] = hashlib.md5(new_event_name.encode()).hexdigest()
    event_data = global_events[context.user_data["newest_event_id"]] = EventData()
    event_data.users.add(update.effective_user)
    event_data.admin = update.effective_user
    event_data.name = new_event_name

    await update.message.reply_text(
        "Nice! Now let's get this party started 🎊\n"
        "<b>Enter item needed for the event:</b>\n",
        parse_mode="HTML",
    )

    return ENTERED_NEW_ITEM


async def handle_new_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_item_name = update.message.text.strip()
    context.user_data["newest_item_name"] = new_item_name
    event_data = global_events[context.user_data["newest_event_id"]]
    event_data.items.append(EventItem(name=new_item_name))

    keyboard = [
        [
            InlineKeyboardButton(
                "Add more of this item", callback_data="add_more_of_the_same_item"
            )
        ],
        [InlineKeyboardButton("Add another item", callback_data="add_another_item")],
        [InlineKeyboardButton("No more items", callback_data="no_more_items")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Great!\n"
        f"<b>Do you need more than 1 {new_item_name}?</b>\n"
        "<b>Or should we move to the next item?</b>\n",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

    return MORE_ITEMS_DECISION


async def handle_more_items_decision(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    decision = query.data

    if decision == "add_more_of_the_same_item":
        await query.edit_message_text(
            text="<b>How many do we need overall:</b>", parse_mode="HTML"
        )
        return ENTERED_MORE_OF_SAME_ITEM
    elif decision == "add_another_item":
        await query.edit_message_text(
            text="<b>Enter item needed for the event:</b>\n",
            parse_mode="HTML",
        )
        return ENTERED_NEW_ITEM
    else:
        await query.edit_message_text(
            text="Nice!\n We have all of our items listed 🔥", parse_mode="HTML"
        )
        return await handle_event_creation_summery(update, context)


async def handle_more_of_same_item(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    async def got_invalid_number():
        await update.message.reply_text(
            text="<b>Invalid number. Try again, how many do we need overall:</b>\n",
            parse_mode="HTML",
        )
        return ENTERED_MORE_OF_SAME_ITEM

    try:
        new_item_count = int(update.message.text)
    except ValueError:
        return got_invalid_number()
    if new_item_count < 1:
        return got_invalid_number()

    event_data = global_events[context.user_data["newest_event_id"]]
    for _ in range(new_item_count - 1):
        event_data.items.append(EventItem(name=context.user_data["newest_item_name"]))

    keyboard = [
        [InlineKeyboardButton("Add another item", callback_data="add_another_item")],
        [InlineKeyboardButton("No more items", callback_data="no_more_items")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Great!\n" "<b>Do we need anything else?</b>\n",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

    return MORE_ITEMS_DECISION


async def handle_event_creation_summery(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    items_text = ", ".join(
        [
            item.name
            for item in global_events[context.user_data["newest_event_id"]].items
        ]
    )
    event_data = global_events[context.user_data["newest_event_id"]]
    summary_text = (
        "<b>Let's go over it ✍️\n</b>"
        "<b>Here's a summery of the Event:\n</b>"
        f"<b>Name:</b> {event_data.name}\n"
        f"<b>Organizer:</b> {event_data.admin.full_name}\n"
        f"<b>Needed Items:</b> {items_text}\n"
        f"<b>Invite Link:</b> https://t.me/EventArchitectBot?start={context.user_data['newest_event_id']}"
    )

    # Determine the correct way to send a reply based on the update type
    if update.callback_query:
        # If called from a callback query, use the callback_query's message
        chat_id = update.callback_query.message.chat_id
        await context.bot.send_message(
            chat_id=chat_id, text=summary_text, parse_mode="HTML"
        )
        # Optionally, you might want to acknowledge the callback query
        await update.callback_query.answer()
    elif update.message:
        # If called from a direct message
        await update.message.reply_text(text=summary_text, parse_mode="HTML")
    else:
        logging.warning(
            "handle_event_creation_summery was called without a message or callback_query context."
        )

    return END


async def handle_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    def get_base_keyboard(event_data: EventData):
        keyboard = [
            [InlineKeyboardButton(item.name, callback_data=str(index))]
            for index, item in enumerate(event_data.items)
            if not item.assigned_user
        ]
        keyboard.append([InlineKeyboardButton("Submit", callback_data="submit")])
        return InlineKeyboardMarkup(keyboard)

    event_data = global_events[context.user_data["newest_event_id"]]
    context.user_data["items_selection"] = list()
    if any([item for item in event_data.items if not item.assigned_user]):
        summary_text = (
            f"Welcome to the event - {event_data.name}\n"
            f"Organized by - {event_data.admin.full_name}\n"
            "Here is what we still need help with, what can you bring?\n"
        )
        await update.message.reply_text(
            text=summary_text, reply_markup=get_base_keyboard(event_data)
        )
        return ENTERED_ITEM_TO_BRING
    else:
        await update.message.reply_text(
            text="Nothing left to bring 😁", parse_mode="HTML"
        )
        return await handle_item_to_bring_summary(update, context)


async def handle_items_to_bring_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    async def get_updated_keyboard(selected: List[str], event_data: EventData):
        keyboard = []
        for i in range(len(event_data.items)):
            text = event_data.items[i].name + (" ✔️" if str(i) in selected else "")
            if not event_data.items[i].assigned_user:
                keyboard.append([InlineKeyboardButton(text, callback_data=str(i))])
        keyboard.append([InlineKeyboardButton("Submit", callback_data="submit")])
        return InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    await query.answer()
    selections = context.user_data["items_selection"]
    event_data = global_events[context.user_data["newest_event_id"]]

    if query.data == "submit":
        if selections:
            for opt in selections:
                event_data.items[int(opt)].assigned_user = query.from_user
            selected_text = ", ".join(
                event_data.items[int(opt)].name for opt in selections
            )
            await query.edit_message_text(f"You selected: {selected_text}")
        else:
            await query.edit_message_text("You didn't select any options.")
        return await handle_item_to_bring_summary(update, context)

    # Track user selections
    if "items_selection" not in context.user_data:
        context.user_data["items_selection"] = list()

    items_selection = context.user_data["items_selection"]
    if query.data not in context.user_data["items_selection"]:
        items_selection.append(query.data)
    else:
        items_selection.remove(query.data)

    # Update the keyboard to reflect current selections
    markup = await get_updated_keyboard(items_selection, event_data)
    await query.edit_message_reply_markup(reply_markup=markup)
    return ENTERED_ITEM_TO_BRING


async def handle_item_to_bring_summary(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    selections = context.user_data["items_selection"]
    event_data = global_events[context.user_data["newest_event_id"]]
    items_text = (
        ", ".join(event_data.items[int(opt)].name for opt in selections)
        if selections
        else "Nothing 🥲"
    )
    summary_text = (
        "<b>Thank you for the cooperation! 🔥\n</b>"
        f"<b>You volunteered to bring: {items_text}\n</b>"
        "<b>See you there!\n</b>"
        f"<b>Event Name:</b> {event_data.name}\n"
        f"<b>Organizer:</b> {event_data.admin.name}\n"
        f"<b>Invite Link:</b> https://t.me/EventArchitectBot?start={context.user_data['newest_event_id']}"
    )

    # Determine the correct way to send a reply based on the update type
    if update.callback_query:
        # If called from a callback query, use the callback_query's message
        chat_id = update.callback_query.message.chat_id
        await context.bot.send_message(
            chat_id=chat_id, text=summary_text, parse_mode="HTML"
        )
        # Optionally, you might want to acknowledge the callback query
        await update.callback_query.answer()
    elif update.message:
        # If called from a direct message
        await update.message.reply_text(text=summary_text, parse_mode="HTML")
    else:
        logging.warning(
            "handle_item_to_bring_summary was called without a message or callback_query context."
        )

    return END
