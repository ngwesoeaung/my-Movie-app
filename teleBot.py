import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    PicklePersistence,
)

# Deletion delay in seconds (24 hours = 86400)
DELETION_DELAY_SECONDS = 86400

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- JobQueue Callback Function ---
async def delete_message_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Callback function for the JobQueue. Deletes the message specified in the job's data.
    """
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    message_id = job_data["message_id"]
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Successfully deleted message {message_id} from chat {chat_id}.")
    except Exception as e:
        logger.error(f"Failed to delete message {message_id} in chat {chat_id}: {e}")


# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command.
    - If it has a payload (from a deep link), it sends videos.
    - Otherwise, it shows the main menu.
    """
    # Check if the command includes a payload (from a deep link)
    if context.args:
        payload = context.args[0]
        logger.info(f"Deep link clicked with payload: {payload}")

        payload_map = {
            'onepiece_1-100': ("Episodes 1-100", 1),
            'onepiece_101-200': ("Episodes 101-200", 101),
            'onepiece_201-300': ("Episodes 201-300", 201),
            'onepiece_301-400': ("Episodes 301-400", 301),
            'onepiece_401-500': ("Episodes 401-500", 401),
            'onepiece_501-600': ("Episodes 501-600", 501),
            'onepiece_601-700': ("Episodes 601-700", 601),
            'onepiece_701-800': ("Episodes 701-800", 701),
            'onepiece_801-900': ("Episodes 801-900", 801),
            'onepiece_901-1000': ("Episodes 901-1000", 901),
            'onepiece_1001-1100': ("Episodes 1001-1100", 1001),
            'onepiece_1101-Ongoing': ("Episodes 1101-Ongoing", 1101),
        }

        if payload in payload_map:
            series_name, start_episode = payload_map[payload]
            await send_video_series(update, context, series_name, start_episode)
        else:
            await update.message.reply_text("Sorry, I don't recognize this link.")

    else:
        # If there's no payload, show the main menu
        keyboard = [
            [InlineKeyboardButton("O-n-e P-iece (1 - 100) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_1-100')],
            [InlineKeyboardButton("O-n-e P-iece (101 - 200) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_101-200')],
            [InlineKeyboardButton("O-n-e P-iece (201 - 300) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_201-300')],
            [InlineKeyboardButton("O-n-e P-iece (301 - 400) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_301-400')],
            [InlineKeyboardButton("O-n-e P-iece (401 - 500) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_401-500')],
            [InlineKeyboardButton("O-n-e P-iece (501 - 600) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_501-600')],
            [InlineKeyboardButton("O-n-e P-iece (601 - 700) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_601-700')],
            [InlineKeyboardButton("O-n-e P-iece (701 - 800) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_701-800')],
            [InlineKeyboardButton("O-n-e P-iece (801 - 900) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_801-900')],
            [InlineKeyboardButton("O-n-e P-iece (901 - 1000) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_901-1000')],
            [InlineKeyboardButton("O-n-e P-iece (1001 - 1100) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_1001-1100')],
            [InlineKeyboardButton("O-n-e P-iece (1101 - Ongoing) ကြည့်ရန် နှိပ်ပါ", callback_data='ep_1101-Ongoing')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_message = ("Hello 👋\n\nကြိုက်နှစ်သက်ရာ Season အလိုက်နှိပ်ပါ။"
                                      "\nMain Channel လေးကိုလဲ Joinထားပေးပါနော်"
                                      "\n@Naruto_MainChannel")
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)


# --- Video Sending Logic ---
async def send_video_series(update: Update, context: ContextTypes.DEFAULT_TYPE, series_name: str, start_episode: int):
    """
    Sends a series of videos and schedules them for deletion.
    """
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=f"Sending {series_name}...")

    # --- VIDEO FILE IDs ---
    # Remember to fill in all your video IDs here!
    video_lists = {
        "Episodes 1-100": [
            "BAACAgQAAxkBAAECL3ZosMc8u3GRo9ZbNzaaODG5PuwongACqwgAAsDuCFBhZ0CFNldFuzYE",
            "BAACAgQAAxkBAAECL3dosMc8ssNO9saWKP0d4CuNxLDIXAACtggAAsDuCFDIboTGOYKrwjYE",
            "BAACAgQAAxkBAAECM_toswsTQVpbchr8dDz6wlclFY3FVQACtwgAAsDuCFBx_NC7OhTU4zYE",
            "BAACAgQAAxkBAAECM_xoswsT1WzFP2Z-azbHz9zjJhwaEwACuggAAsDuCFD7SnwM4BDw3DYE",
            "BAACAgUAAxkBAAECM_1oswsTrZojnd53dX4auCwl9hBhswACQAQAAmv5CFe-fWdjwURayjYE",
            "BAACAgUAAxkBAAECM_5oswsTbev67fIFlvd9r56FNws42QACRQQAAmv5CFebx4HTFGWSojYE",
            "BAACAgUAAxkBAAECM_9oswsTUtOu8PVxGtJACPypn6PWqQACRgQAAmv5CFd5PkurGnyO7TYE",
            "BAACAgUAAxkBAAECNAABaLMLE_m1HFuzOsxQrd6gHIPA0B4AAkgEAAJr-QhXcqPCPnGThCA2BA",
            "BAACAgUAAxkBAAECNAFoswsTXi4cyB1lMgYvAbfpFxIlzgACSQQAAmv5CFfvGa02NedtDzYE",
            "BAACAgUAAxkBAAECNAJoswsTyZDOSLTNBQsAATvE9a-P16IAAkoEAAJr-QhXjDiohOvxDqQ2BA",
            "BAACAgUAAxkBAAECNBZoswxPCjWQmRBsL6SNgsgDPa-ZwQACogIAAmv5EFfnjoaY9Bqm2jYE",
            "BAACAgUAAxkBAAECNBdoswxPd5zSKsLpavk0OD8CX4o8ggAC3wIAAmv5EFcsA2oUm9_gbDYE",
            "BAACAgUAAxkBAAECNBhoswxPeewOm2BFX4BXnB0m7WI7wAAC5AIAAmv5EFcTYX0sUUOH6zYE",
            "BAACAgUAAxkBAAECNBloswxPXBzMIQnAop_h1YjfVg8WmgACCAMAAmv5EFfZKDDHAlxcizYE",
            "BAACAgUAAxkBAAECNBposwxPaSqypKJnKo-bZf99wvPKRgACCQMAAmv5EFfoy00DMPUWxTYE",
            "BAACAgUAAxkBAAECNBtoswxPshKyaXNs22sjdPfE0vFPKAACGQMAAmv5EFed10L0g-9GYTYE",
            "BAACAgUAAxkBAAECNBxoswxPyU_aju3vAeGsNZ4doOLNkgACKAMAAmv5EFcZx-12OHap6TYE",
            "BAACAgUAAxkBAAECNB1oswxPnzlHqnQsCjMov0dBLqvZQQACKQMAAmv5EFc0Q5G9PL6XJDYE",
            "BAACAgUAAxkBAAECNB5oswxPUzxG9Pi9OEuqOhsVVY6_5QACGQIAApD8IVd-llBgx4hVRjYE",
            "BAACAgUAAxkBAAECNB9oswxP7BctAAFgpyqtZShg25GP7MAAAh0CAAKQ_CFXPSFJUnAk0cw2BA",
            "BAACAgUAAxkBAAECNDhosw18906SXGjEhclO0vR6CaYgIAACHgIAApD8IVcLxN3QkPct8zYE",
            "BAACAgUAAxkBAAECNDlosw18RI5_qyEq_A1r3etL1sDgXQACMAMAAtElCFSwm4oQxP2P0DYE",
            "BAACAgQAAxkBAAECNDposw18LZF14f7bNg1gKDJl3R2utgACzggAAsDuCFByJ2h8qow3ojYE",
            "BAACAgUAAxkBAAECNDtosw18p9ms0PcNLb9imUEnueNuswACMgMAAtElCFRzK17oDuOyMjYE",
            "BAACAgUAAxkBAAECNDxosw184G6cTnYG5qM8Rx7qxZ9pigACMwMAAtElCFR0KwokAAE_4Q42BA",
            "BAACAgQAAxkBAAECND1osw18PRLMxZdB9TSj1IAhc4vsHQAC5AgAAsDuCFD_bqOB1pPJ0jYE",
            "BAACAgUAAxkBAAECND5osw18Qs6kDyiZRW0w-O3qzKKJTwACNAMAAtElCFSY0g_h-hcMJzYE",
            "BAACAgUAAxkBAAECND9osw18li_K4hAXqtasKugJRlSGXgACNQMAAtElCFSsvxiU5eyxSDYE",
            "BAACAgQAAxkBAAECNEBosw18t7QAAakyr7CPc0eXnSvprowAAhUJAALA7ghQZbmV40LzsAABNgQ",
            "BAACAgUAAxkBAAECNEFosw18v3NT1UBMt-XJapaJ-qQxkgACNgMAAtElCFTg9zF4V2cKyzYE",
            "BAACAgUAAxkBAAECNFBosw6ots95s0DVnlfibk1apu3YTAACOAMAAtElCFRpyiLJnWPHpjYE",
            "BAACAgUAAxkBAAECNFFosw6oa-KsaWwSxxbrm29sYXOmFQACOQMAAtElCFTg-0hovdRjlzYE",
            "BAACAgUAAxkBAAECNFJosw6oj76SdJZAEWsB0gK3NZsEFAACOwMAAtElCFTp76pH6DypVzYE",
            "BAACAgUAAxkBAAECNFNosw6oNUofS3o0Ha5idHKjBW-XFQACOgMAAtElCFRJZKtl_gO63zYE",
            "BAACAgUAAxkBAAECNFRosw6oyZ7h8nhedkte5dtmpfZuZgACPAMAAtElCFT3NBxVoF_N3zYE",
            "BAACAgUAAxkBAAECNFVosw6oWszHHRlprP3KiwUTj-eBBwACPgMAAtElCFT1rmsHa9jNTjYE",
            "BAACAgUAAxkBAAECNFZosw6oR4ZUYHRBgp51CkD1dFdPuAACPwMAAtElCFTIKESF3h2D8jYE",
            "BAACAgUAAxkBAAECNFdosw6oVkFQG8j4OuVLCXaW2Ow4hgACQAMAAtElCFTEmDUVpEyXjTYE",
            "BAACAgUAAxkBAAECNFhosw6oFLMjaGc5lPMcMYWFLudvKwACQQMAAtElCFSDzeDj77MG8zYE",
            "BAACAgUAAxkBAAECNFlosw6ooHv0ZSbQt3-ZFCjOqWViFAACQgMAAtElCFSvj6JUdo-LgjYE",
            "BAACAgUAAxkBAAECNGposxB7Bx-gRUqULxF5wwGAtOIpogACQwMAAtElCFTIxGG9v8qCgzYE",
            "BAACAgUAAxkBAAECNGtosxB71FP96vAlYcosFDt6NtP83wACRQMAAtElCFSW2b9P09DZ8jYE",
            "BAACAgUAAxkBAAECNGxosxB7xpmtqTCL-hQqoi4QsQh5gAACRAMAAtElCFSnOEkjeFPO-zYE",
            "BAACAgUAAxkBAAECNG1osxB7_oInMOR2713CGfs394EG_gACRwMAAtElCFS44M_3vwMnOjYE",
            "BAACAgUAAxkBAAECNG5osxB7ngJDSREEgxq3fSYiR32ebAACRgMAAtElCFRbsDtAdhtF9DYE",
            "BAACAgUAAxkBAAECNG9osxB71zZrl8CeeBQq2s6w-DggCAACSAMAAtElCFTENusZGK_iJDYE",
            "BAACAgUAAxkBAAECNHBosxB7OyNa-_DiCmoS_9PpuVFP-AACSQMAAtElCFQGAiQ9RHjkeTYE",
            "BAACAgUAAxkBAAECNHFosxB7hvn5txUVnxpIaJMh7PTxWwACSwMAAtElCFSfavIcSitshzYE",
            "BAACAgUAAxkBAAECNHJosxB7JBU53_mEgFZ9Wel18zjd3gACSgMAAtElCFSxUUtwTuN-7jYE",
            "BAACAgUAAxkBAAECNHNosxB7PGLAwDBswPzrR0vNfZieFQACTAMAAtElCFRQl3a296MggTYE",
            "BAACAgUAAxkBAAECNH5osxGTFMUy1IMFYgpck78ngKM5DQACTQMAAtElCFTFtE5O8o1NjTYE",
            "BAACAgUAAxkBAAECNH9osxGT6eJP03Qh1rEoefgNgF4eAANOAwAC0SUIVE1pVSL7vO5cNgQ",
            "BAACAgUAAxkBAAECNIBosxGTI5yoj2rn3FlKWIFyVROydAACUAMAAtElCFRA2zZP4TxOJDYE",
            "BAACAgUAAxkBAAECNIFosxGTaSyyeOZP0MmsNhyKYXDuCQACUQMAAtElCFTHkHHBNQRWoDYE",
            "BAACAgUAAxkBAAECNIJosxGTvGXYcsH3CTtuCRQbPMFIhwACTwMAAtElCFSYs4OvJxOTHDYE",
            "BAACAgUAAxkBAAECNINosxGTTEKcIO_JYgHxhXvolIoPQQACUgMAAtElCFRDwdVQLgoicTYE",
            "BAACAgUAAxkBAAECNIRosxGTb_5b35uObR44xfLtqPcFGwACUwMAAtElCFSIKTxsti5DjDYE",
            "BAACAgUAAxkBAAECNIVosxGTmGau9-ffPqqKBr_jqdpGkQACVAMAAtElCFQMDXrh7TREyjYE",
            "BAACAgUAAxkBAAECNIZosxGTLoAujl8SIVJ15zBRI3UTDgACVQMAAtElCFSbmMFUDoK2rTYE",
            "BAACAgUAAxkBAAECNIdosxGTMZyt0WXfkpU9XoXWrXIvxAACVgMAAtElCFRgNupaYapRRTYE",
            "BAACAgUAAxkBAAECNIhosxGTQ6Afwzrx-zrDtCtJ0wi3yAACWAMAAtElCFQtCuq94HC2jzYE",
            "BAACAgUAAxkBAAECNIlosxGTqvnm0SHtCscpRU01t8TCXAACWgMAAtElCFQG0zjBWtcibTYE",
            "BAACAgUAAxkBAAECNIposxGTamt8b1szJbF1whhawBUW9AACVwMAAtElCFTi2FP877kPuzYE",
            "BAACAgUAAxkBAAECNIxosxGTAAFBRnhXN1YrrSvs6IBUG1EAAlkDAALRJQhUp-8r3L8QBzE2BA",
            "BAACAgUAAxkBAAECNI1osxGTRH4NAwOabnIDpulBpx0g9AACXAMAAtElCFQ7D9v71i6I_zYE",
            "BAACAgUAAxkBAAECNI5osxGTpw15x46tMC0pDrMoKuhxTAACWwMAAtElCFQvJYqZCZ2HbDYE",
            "BAACAgUAAxkBAAECNI9osxGTJUq7Rr9fs0QCBpnh22nq0QACXQMAAtElCFQEzaYe6zhnJDYE",
            "BAACAgUAAxkBAAECNJBosxGTAAGjKmQ9ggnvIn9RA968q7IAAl8DAALRJQhUhp5rIl_rkfg2BA",
            "BAACAgUAAxkBAAECNJFosxGUPlL4p02YmLa2q2O3nldkmAACXgMAAtElCFQ34HfuCa2DszYE",
            "BAACAgUAAxkBAAECNJJosxGUiflrLrCW0-1u4SDSa1egqAACYAMAAtElCFRL24KMMuT8cTYE",
            "BAACAgUAAxkBAAECNJNosxGUjhNI6D0EEJ26Cdm3XyqEJgACYQMAAtElCFS0u3-08ux57DYE",
            "BAACAgUAAxkBAAECNJRosxGU-vABWsUmb3_WU6XsPpAXFQACYgMAAtElCFSxvlJGwr931jYE",
            "BAACAgUAAxkBAAECNJVosxGUT5VKsB2BPu9NLuPiKyShoQACYwMAAtElCFTef5nXn8ZGTDYE",
            "BAACAgUAAxkBAAECNJZosxGUNMaXtmBl3m_K3C-D--sCTAACZAMAAtElCFTPkU_THXYh1TYE",
            "BAACAgUAAxkBAAECNJdosxGUp-vhvH17lB0kfcJOuHuGZgACZQMAAtElCFSmLdVepQJ1dDYE",
            "BAACAgUAAxkBAAECNJhosxGUxZDiyi7inBLRj5dUuTlcjQACagMAAtElCFQM3T-OvdcB0zYE",
            "BAACAgUAAxkBAAECNJlosxGUw_D7XpkBm9LFgBIlg3DTlQACZwMAAtElCFQ7MCsS7gFJ4DYE",
            "BAACAgUAAxkBAAECNJtosxGU9R3XOzt2KHYcMI5k0mXQLQACaQMAAtElCFSgPIOJirnPuTYE",
            "BAACAgUAAxkBAAECNJxosxGUnoDGn6zwjPE-z6LQsegeSAACaAMAAtElCFTZ-XubbVCjujYE",
            "BAACAgUAAxkBAAECNJ1osxGUsoAxw7RNDzb2H88ahyiA-gACbAMAAtElCFTpnQg77nXyNTYE",
            "BAACAgUAAxkBAAECNJ5osxGUgkZdPGctZt-zGEWlKcrengACbgMAAtElCFRj1Bo0Lim0cTYE",
            "BAACAgUAAxkBAAECNJ9osxGU5IOx3nUY2YHWCLAzBUwNAwACawMAAtElCFS1ZAxkYLBZTTYE",
            "BAACAgUAAxkBAAECNKBosxGUnoZ0Y5ie5ZdBW1_9Wbn0bwACbwMAAtElCFT4tGK2UKZ7FjYE",
            "BAACAgUAAxkBAAECNKFosxGUL7Z5b15a2GvQfDetSokm7wACcQMAAtElCFRobHPKohbrjDYE",
            "BAACAgUAAxkBAAECNKJosxGURF6WtaXsO8rvuKYBGezMQwACcwMAAtElCFQv--57NQ7-ZTYE",
            "BAACAgUAAxkBAAECNKNosxGUKiJQCwr8b3MvQP7cP_LZSQACdQMAAtElCFQnu7G7ir5qXzYE",
            "BAACAgUAAxkBAAECNKRosxGU-iSLFo2IYTCYF7uBF55LswACdAMAAtElCFQjcx-A0qpyTTYE",
            "BAACAgUAAxkBAAECNKVosxGU6aC-82TB8Hz7QxChhN5bLgACcgMAAtElCFT2ZF-L8Bjr0jYE",
            "BAACAgUAAxkBAAECNKZosxGU8zqTmO8Nryrp449K_k9utwACdgMAAtElCFTuo_CwGOHNpTYE",
            "BAACAgUAAxkBAAECNKdosxGU-wVAf_gcAmg5QTZ6307_JQACeQMAAtElCFRBvpzoFPvE8zYE",
            "BAACAgUAAxkBAAECNKhosxGUUP_HMU92TeRwUgp6vIdy9gACdwMAAtElCFRq0Mq_Pg-j3DYE",
            "BAACAgUAAxkBAAECNKposxGUBDctPpCfjSSSK6ux6_9ngwACeAMAAtElCFSa0sjcZTlsZTYE",
            "BAACAgUAAxkBAAECNKtosxGU2eUY4w_T4tJ8L7cwX7UFpAACegMAAtElCFQ7vnl0f8mo1jYE",
            "BAACAgUAAxkBAAECNKxosxGUUopRKIMsndLOjFNkoWCeQwACfQMAAtElCFSljhj_0RUXmzYE",
            "BAACAgUAAxkBAAECNK1osxGUWcR1aVA9zuXRhKZlU-cMSwACewMAAtElCFT7p3qe3oVkjTYE",
            "BAACAgUAAxkBAAECNK5osxGU5-SvVLiyei-LBWFfDvHZBwACfAMAAtElCFSb9Wvy7EcZyDYE",
            "BAACAgUAAxkBAAECNK9osxGUQx33hVWJHc9BSPDPcDBG9QACfgMAAtElCFT65rf8CUJ51TYE",
            "BAACAgUAAxkBAAECNLBosxGUf_wVMGNcR_k2ocDmNhR7pgACgQMAAtElCFRqyLGXzXKH9DYE",
            "BAACAgUAAxkBAAECNLFosxGUyinhJhWdsEBHdmg03vxK_AACgAMAAtElCFSF6ekrVqxukTYE",
            "BAACAgUAAxkBAAECL6NosOPe5Wh9LY_2OuFFhaladB7qQAACfwMAAtElCFSesM6RHH6A8DYE",
        ],
        "Episodes 101-200": [
            "BAACAgUAAxkBAAECL6RosOPeiOYS9WXw_P-HcBUquU2cXwACggMAAtElCFQIASrMxZ9CAAE2BA",
            "BAACAgUAAxkBAAECL8RosOtKsCGRQoeMfTPgXDw5rwZipwAChAMAAtElCFSoxg5HYX54rzYE"
        ],
        "Episodes 201-300": [
            "BAACAgUAAxkBAAECMPhosXwwKklH_Y6JWhYe55JCz6m2FwACWgQAAtElEFS807I684w6fzYE",
            "BAACAgUAAxkBAAECMPlosXww0dsCuoprMJWZd0RkXhRytQACrwQAAtElEFQ_VycAAaentvs2BA"
        ],
        "Episodes 301-400": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 401-500": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 501-600": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 601-700": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 701-800": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 801-900": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 901-1000": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 1001-1100": [
            "Your_Video_ID",
            "Your_Video_ID",
            ],
        "Episodes 1101-Ongoing": [
            "Your_Video_ID",
            "Your_Video_ID"
            ],
    }

    video_ids = video_lists.get(series_name, [])

    if not video_ids or "YOUR_VIDEO_ID_HERE" in video_ids:
        logger.warning(f"No video IDs found or placeholders present for series: {series_name}")
        await context.bot.send_message(chat_id=chat_id, text=f"Sorry, no videos are available for {series_name} yet.")
        return

    for i, video_id in enumerate(video_ids, start=start_episode):
        try:
            # Send the video and store the returned message object
            sent_message = await context.bot.send_video(
                chat_id=chat_id,
                video=video_id,
                caption=(
                    f"Episode {i}\n\n"
                    "(Copyright ကြောင့် 24 Hours အတွင်းပြန်ဖျက်ပါမယ်)\n"
                    "(_____ /start နှိပ်ပြီး ကြည့်ပေးပါရန် _____)\n\n"
                    "1xBet/MLBB Diamond\n"
                    "ထည့်ရန် အောက်က BOT မှာ\n"
                    "အားပေးလို့ရပါတယ်ဗျ\n"
                    "@NSA_Game_Shopbot"
                )
            )

            # Schedule the message for deletion using the config variable
            context.job_queue.run_once(
                delete_message_callback,
                when=DELETION_DELAY_SECONDS,
                data={"chat_id": chat_id, "message_id": sent_message.message_id},
                name=f"delete_{chat_id}_{sent_message.message_id}"
            )
            # Add a small delay to avoid hitting Telegram's rate limits
            await asyncio.sleep(0)
        except Exception as e:
            logger.error(f"Failed to send video {video_id} for episode {i}: {e}")


# --- Button Click Handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button clicks by generating and sending a deep link message."""
    query = update.callback_query
    await query.answer() # Acknowledge the button press

    bot_username = (await context.bot.get_me()).username

    button_map = {
        'ep_1-100': ('onepiece_1-100', "Episodes 1-100"),
        'ep_101-200': ('onepiece_101-200', "Episodes 101-200"),
        'ep_201-300': ('onepiece_201-300', "Episodes 201-300"),
        'ep_301-400': ('onepiece_301-400', "Episodes 301-400"),
        'ep_401-500': ('onepiece_401-500', "Episodes 401-500"),
        'ep_501-600': ('onepiece_501-600', "Episodes 501-600"),
        'ep_601-700': ('onepiece_601-700', "Episodes 601-700"),
        'ep_701-800': ('onepiece_701-800', "Episodes 701-800"),
        'ep_801-900': ('onepiece_801-900', "Episodes 801-900"),
        'ep_901-1000': ('onepiece_901-1000', "Episodes 901-1000"),
        'ep_1001-1100': ('onepiece_1001-1100', "Episodes 1001-1100"),
        'ep_1101-Ongoing': ('onepiece_1101-Ongoing', "Episodes 1101-Ongoing"),
    }

    if query.data in button_map:
        payload, button_text = button_map[query.data]
        deep_link = f"https://t.me/{bot_username}?start={payload}"
        message_text = (
            f"{button_text} ကို ကြည့်ရန် အောက်က link ကိုနှိပ်ပါ။\n\n"
            f"{deep_link}"
        )
        await context.bot.send_message(chat_id=query.message.chat_id, text=message_text)
        

# --- Main Bot Function (UPDATED FOR RENDER) ---
def main() -> None:
    """Starts the bot in webhook mode for server or polling mode for local."""
    token =("7893558945:AAG-DGexBsIh6cAGWaWI92rxzTW1O8CWhSs")
    if not token:
        logger.critical("FATAL: TELEGRAM_TOKEN environment variable not set!")
        return
    
    # NEW: Use an environment variable for the persistence file path
    # This allows us to place it on a persistent disk on Render
    persistence_path = os.environ.get("PERSISTENCE_PATH", "bot_persistence")
    persistence = PicklePersistence(filepath=persistence_path)

    application = Application.builder().token(token).persistence(persistence).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # --- NEW: Webhook vs. Polling Logic ---
    webhook_url = os.environ.get("RENDER_EXTERNAL_URL")
    if webhook_url:
        # Running on Render (or any server with this env var)
        port = int(os.environ.get("PORT", 8443))
        logger.info(f"Starting bot in webhook mode on port {port}")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token, # Use token as a secret path
            webhook_url=f"{webhook_url}/{token}"
        )
    else:
        # Running locally
        logger.info("Starting bot in polling mode for local development")
        application.run_polling()


if __name__ == "__main__":
    main()