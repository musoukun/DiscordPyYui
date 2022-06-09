import random
# インストールした discord.py を読み込む
import discord
import youtube_dl
import asyncio
import os
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system
#googleSearch
import googlesearch
from googlesearch import search
import datetime
import shutil

# Botのアクセストークン(操作対象のBOTのトークンを指定）
TOKEN = ''

BOT_PREFIX = "/"

# 接続に必要なオブジェクトを生成
client = discord.Client()
#bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"))
bot = commands.Bot(command_prefix=BOT_PREFIX)
songs = asyncio.Queue()
play_next_song = asyncio.Event()
queues = {}

##########  定数  ###########

CHANNEL_ID = 711166774053306388 # 自分のチャンネルID(int)
#CHANNEL_ID = 708668194344402947 # アニメかいのチャンネルID(int)
ID_CHANNEL_WELCOME = 711166774053306388 # テストチャンネルのID(int)
#ID_ROLE_WELCOME = 708692268558843914 # 付けたい役職のID(int)
#EMOJI_WELCOME = '' # 対応する絵文字

youtube_url = 'https://youtu.be/2SvspexYSb0?t=4' # youtubeのURLを指定 (YUIちゃんのボイス)
#discord_voice_channel_id = 653273189467553822 # 特定のボイスチャンネルを指定

voice = None
channel = None
loginC = 0 #loginしましたフラグ

@bot.event
async def on_ready():
    global loginC
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    if loginC !=1:
      await greet() #入室時の発言
    loginC = 1 

# 返信の非同期関数
async def reply(message, chat):
    if chat == '0':
        comment = ["こんにちは。ユイです。"
                , "このプレイヤーIDは間違いなくママのものです！"
                #, "わかりました！記録しておきますね。"
                , "私はどうやらサポート用のピクシーに分類されているようです。少しだけですけど、この世界でパパのサポートが出来そうです。"
                , "え～！新しい人とパーティを組むんですか？ならわたしのこともきちんと紹介してくださいよ！ よろしくお願いしますね"
                , "あの…ちょっと聞いてもいいですか？ パパのいる世界ってどんな世界なんですか？私、パパのいるもう一つの世界を見てみたいなって思う事があるんです。変ですよね？ごめんなさい…。"
                , "おつかれさまです。パパ。"
                ]
        choice = random.choice(comment) #randomモジュール使用
        ment = f'{message.author.mention}'   
        await message.channel.send(ment + choice)
    elif chat == 'hello':
        reply = f'{message.author.mention} こんにちは。ユイです。' # 返信メッセージの作成
        await message.channel.send(reply) # 返信メッセージを送信
    elif chat == 'GJ':
        reply = f'{message.author.mention} おつかれさまです。パパ。' # 返信メッセージの作成
        await message.channel.send(reply) # 返信メッセージを送信
    elif chat == 'How':
        file = discord.File("C:\discord\img\yui.png", filename="image.png")
        embed = discord.Embed(title="パパとママとずっと一緒",description="ユイの思い出です！")
        embed.set_image(url="attachment://yui.png")
        await message.channel.send(embed=embed, file=file)
    
# 任意のチャンネルで挨拶する非同期関数
async def greet():
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('こんにちは。ユイです。')

@bot.event
# 発言時に実行されるイベントハンドラ
async def on_message(message):
    msg = message.clean_content
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    if 'こんにちは' in msg:
        chat = 'hello'
    elif 'おつかれ' in msg:
        chat = 'GJ'
    elif '思い出' in msg:
        chat = 'How'
    else:    
        chat = '0'

    if bot.user in message.mentions: # 話しかけられたかの判定
        await reply(message, chat) # 返信する非同期関数を実行
    
    await bot.process_commands(message) #Commands競合回避

# 新規メンバー参加時に実行されるイベントハンドラ(member引数)
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(member.guild._system_channel_id)
    role = discord.utils.get(member.guild.roles, name='kuwa㌠')
    if not role:
        await channel.send(str(member.mention) + 'さん ようこそ！')
    else:
        await member.add_roles(role)
        await channel.send(str(member.mention) + 'さん アニメ会にようこそ！　kuwa㌠の権限を付与しました。')

##########  コマンド  ###########
@bot.command(name='yuic')
async def yuic(ctx):
    global voice, channel
        
    voice = get(bot.voice_clients, guild=ctx.guild)

    if ctx.message.author.voice is None: #voiceがない→未入室
        await ctx.send('まずはパパがボイスチャンネルに参加してください！')
        return
    else:
        channel = ctx.message.author.voice.channel #入室ボイチャ確認
    
    if voice and voice.is_connected():
        # 再生中の場合は一度停止
        if(voice.is_playing()):
            voice.stop()
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    print(f"YUIが {channel}\n に接続しました！")
    await ctx.send(f"YUIが {channel}\n に接続しました！")

    #await voice.disconnect()

    # ボイスチャンネルIDを指定する場合に使う↓
    #if discord_voice_channel_id == '':
    # ボイスチャンネルIDが指定されていたら
    #else:
        #await discord.VoiceChannel.connect(bot.get_channel(discord_voice_channel_id))
        #print(f"YUIが {channel}\n に接続しました！")
        #await ctx.send(f"YUIが {channel}\n に接続しました！")

@bot.command()
async def yuip(ctx, url: str = youtube_url):

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("まだ音声が再生中のようです。")
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    voice_client = ctx.message.guild.voice_client
    
    # 接続済みか確認
    if not voice_client:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("わたしはボイスチャンネルにいません...。")
        return

    await ctx.send("音声を準備しています。")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"),  after=lambda e: print('song done!'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.5

    nname = name.rsplit("-", 2)
    if url != youtube_url:
        await ctx.send(f"YUIがYouTubeから{nname[0]}を再生します！")
    else:
        await ctx.send(f"パパとの思い出を振り返りましょう！")
    print("playing\n")



@bot.command()
async def yuil(ctx):
    if ctx.message.author.voice != None:
        channel = ctx.message.author.voice.channel

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"ユイは {channel} を出ますね！また呼んでください、パパ。")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("わたしはボイスチャンネルにいません...。")

@bot.command()
async def stop(ctx):
    #if ctx.message.author.voice != None:
    #    channel = ctx.message.author.voice.channel
    #
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        if voice.is_playing():
            await voice.pause()
            print(f"The bot pause voice")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("わたしはボイスチャンネルにいません...。")

@bot.command()
async def play(ctx):
    if ctx.message.author.voice != None:
        channel = ctx.message.author.voice.channel

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        if voice and voice.is_paused():
            await voice.resume()
            print(f"The bot pause voice")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("わたしはボイスチャンネルにいません...。")
#入力まち↓
@bot.command()
async def gs(ctx):
    await ctx.send('検索ワードを教えてください。')
    try:
        msg = await bot.wait_for('message', timeout=60.0)
    except asyncio.TimeoutError:
        await channel.send('必要な時はまた呼んでください。')
    else:
        kensaku = msg.clean_content
        await ctx.send(kensaku + 'を1件検索します。')
        for url in search(kensaku, lang="jp",stop = 1):
            await ctx.send(url)

@bot.command()
async def gsa(ctx ,kensaku :str = '今期'):

    word = 'アニメ一覧 animatetimes'
    if kensaku == '今期':
        now = datetime.date.today()
        if 1 <= now.month < 3:
            konki = '冬'
        elif 4 <= now.month < 6:
            konki = '春'
        elif 7 <= now.month < 9:
            konki = '夏'
        elif 10 <= now.month < 12:
            konki = '秋'
        kensaku = str(now.year)
        kensaku = kensaku + konki + word
    else:
        kensaku = kensaku + word
    
    await ctx.send(kensaku + 'を検索します')
            
    for url in search(kensaku, lang="jp",stop = 1):
        await ctx.send(url)

############## 接続 ################
# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)
#client.run(TOKEN)


