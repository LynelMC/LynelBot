import discord
from discord import app_commands
from discord.ext import commands
from storage import storage
import re
import datetime

# Embedに付与するボタンの基底クラス
class EmbedLinkButton(discord.ui.Button):
    def __init__(self, label: str, url: str, style: discord.ButtonStyle = discord.ButtonStyle.link):
        super().__init__(label=label, style=style, url=url)

# Embed作成用のModal
class EmbedTextModal(discord.ui.Modal, title="Embedのタイトルと説明"):
    title_input = discord.ui.TextInput(label="タイトル", placeholder="Embedのタイトル", required=False, max_length=256)
    description_input = discord.ui.TextInput(label="説明文", style=discord.TextStyle.paragraph, placeholder="Embedの説明文 (Markdown対応)", required=False, max_length=4000)

    def __init__(self, current_data):
        super().__init__()
        self.title_input.default = current_data.get("title", "")
        self.description_input.default = current_data.get("description", "")

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        storage.set_guild_data(guild_id, "embed_title", self.title_input.value)
        storage.set_guild_data(guild_id, "embed_description", self.description_input.value)
        await interaction.response.send_message("タイトルと説明を保存しました。", ephemeral=True)

class EmbedImageModal(discord.ui.Modal, title="Embedの画像設定"):
    image_url_input = discord.ui.TextInput(label="メイン画像URL (任意)", placeholder="https://example.com/image.png", required=False)
    thumbnail_url_input = discord.ui.TextInput(label="サムネイル画像URL (任意)", placeholder="https://example.com/thumbnail.png", required=False)

    def __init__(self, current_data):
        super().__init__()
        self.image_url_input.default = current_data.get("image_url", "")
        self.thumbnail_url_input.default = current_data.get("thumbnail_url", "")

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        storage.set_guild_data(guild_id, "embed_image_url", self.image_url_input.value)
        storage.set_guild_data(guild_id, "embed_thumbnail_url", self.thumbnail_url_input.value)
        await interaction.response.send_message("画像設定を保存しました。", ephemeral=True)

class EmbedFooterModal(discord.ui.Modal, title="Embedのフッター設定"):
    footer_text_input = discord.ui.TextInput(label="フッターテキスト (任意)", placeholder="フッターのテキスト", required=False, max_length=2048)
    footer_icon_url_input = discord.ui.TextInput(label="フッターアイコンURL (任意)", placeholder="https://example.com/icon.png", required=False)

    def __init__(self, current_data):
        super().__init__()
        self.footer_text_input.default = current_data.get("footer_text", "")
        self.footer_icon_url_input.default = current_data.get("footer_icon_url", "")

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        storage.set_guild_data(guild_id, "embed_footer_text", self.footer_text_input.value)
        storage.set_guild_data(guild_id, "embed_footer_icon_url", self.footer_icon_url_input.value)
        await interaction.response.send_message("フッター設定を保存しました。", ephemeral=True)

class EmbedButtonModal(discord.ui.Modal, title="Embedボタン設定"):
    button_label_input = discord.ui.TextInput(label="ボタンのラベル", placeholder="クリック！", required=True, max_length=80)
    button_url_input = discord.ui.TextInput(label="ボタンのURL", placeholder="https://example.com", required=True)

    def __init__(self, button_index=None, current_data=None):
        super().__init__()
        self.button_index = button_index
        if current_data:
            self.button_label_input.default = current_data.get("label", "")
            self.button_url_input.default = current_data.get("url", "")

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        buttons = storage.get_setting(guild_id, "embed_buttons", [])
        new_button = {"label": self.button_label_input.value, "url": self.button_url_input.value}

        if self.button_index is not None and self.button_index < len(buttons):
            buttons[self.button_index] = new_button
            message = f"ボタン {self.button_index + 1} を更新しました。"
        else:
            buttons.append(new_button)
            message = "ボタンを追加しました。"
        
        storage.set_guild_data(guild_id, "embed_buttons", buttons)
        await interaction.response.send_message(message, ephemeral=True)

class EmbedButtonManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    @discord.ui.button(label="ボタンを追加", style=discord.ButtonStyle.success, custom_id="add_embed_button")
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedButtonModal())

    @discord.ui.button(label="ボタンを編集/削除", style=discord.ButtonStyle.secondary, custom_id="edit_remove_embed_button")
    async def edit_remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        buttons = storage.get_setting(guild_id, "embed_buttons", [])

        if not buttons:
            return await interaction.response.send_message("設定されているボタンがありません。", ephemeral=True)

        options = []
        for i, btn_data in enumerate(buttons):
            options.append(discord.SelectOption(label=f"ボタン {i+1}: {btn_data['label']}", value=str(i)))
        
        select = discord.ui.Select(placeholder="編集または削除するボタンを選択", options=options, custom_id="select_embed_button_to_edit")

        async def select_callback(interaction: discord.Interaction):
            selected_index = int(select.values[0])
            selected_button_data = buttons[selected_index]

            edit_button = discord.ui.Button(label="編集", style=discord.ButtonStyle.primary, custom_id=f"edit_embed_button_{selected_index}")
            delete_button = discord.ui.Button(label="削除", style=discord.ButtonStyle.danger, custom_id=f"delete_embed_button_{selected_index}")

            async def edit_callback(interaction: discord.Interaction):
                await interaction.response.send_modal(EmbedButtonModal(button_index=selected_index, current_data=selected_button_data))

            async def delete_callback(interaction: discord.Interaction):
                buttons.pop(selected_index)
                storage.set_guild_data(guild_id, "embed_buttons", buttons)
                await interaction.response.send_message(f"ボタン {selected_index + 1} を削除しました。", ephemeral=True)

            edit_button.callback = edit_callback
            delete_button.callback = delete_callback

            temp_view = discord.ui.View(timeout=60)
            temp_view.add_item(edit_button)
            temp_view.add_item(delete_button)
            await interaction.response.send_message(f"ボタン {selected_index + 1} の操作を選択してください。", view=temp_view, ephemeral=True)

        select.callback = select_callback
        temp_view = discord.ui.View(timeout=60)
        temp_view.add_item(select)
        await interaction.response.send_message("どのボタンを操作しますか？", view=temp_view, ephemeral=True)

class EmbedSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    async def _get_current_embed(self, guild_id: int) -> discord.Embed:
        title = storage.get_setting(guild_id, "embed_title")
        description = storage.get_setting(guild_id, "embed_description")
        color_hex = storage.get_setting(guild_id, "embed_color", "#3498db") # Default blue
        image_url = storage.get_setting(guild_id, "embed_image_url")
        thumbnail_url = storage.get_setting(guild_id, "embed_thumbnail_url")
        footer_text = storage.get_setting(guild_id, "embed_footer_text")
        footer_icon_url = storage.get_setting(guild_id, "embed_footer_icon_url")
        use_timestamp = storage.get_setting(guild_id, "embed_timestamp", False)

        embed = discord.Embed(
            title=title if title else discord.Embed.Empty,
            description=description if description else discord.Embed.Empty,
            color=discord.Color.from_str(color_hex)
        )
        if image_url: embed.set_image(url=image_url)
        if thumbnail_url: embed.set_thumbnail(url=thumbnail_url)
        if footer_text or footer_icon_url: embed.set_footer(text=footer_text, icon_url=footer_icon_url)
        if use_timestamp: embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        return embed

    @discord.ui.button(label="タイトル・説明設定", style=discord.ButtonStyle.primary, custom_id="embed_set_text")
    async def set_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        current_data = {
            "title": storage.get_setting(guild_id, "embed_title"),
            "description": storage.get_setting(guild_id, "embed_description")
        }
        await interaction.response.send_modal(EmbedTextModal(current_data))

    @discord.ui.button(label="画像・サムネイル設定", style=discord.ButtonStyle.primary, custom_id="embed_set_image")
    async def set_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        current_data = {
            "image_url": storage.get_setting(guild_id, "embed_image_url"),
            "thumbnail_url": storage.get_setting(guild_id, "embed_thumbnail_url")
        }
        await interaction.response.send_modal(EmbedImageModal(current_data))

    @discord.ui.button(label="フッター設定", style=discord.ButtonStyle.primary, custom_id="embed_set_footer")
    async def set_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        current_data = {
            "footer_text": storage.get_setting(guild_id, "embed_footer_text"),
            "footer_icon_url": storage.get_setting(guild_id, "embed_footer_icon_url")
        }
        await interaction.response.send_modal(EmbedFooterModal(current_data))

    @discord.ui.select(placeholder="色を選択", custom_id="embed_set_color",
                       options=[
                           discord.SelectOption(label="青", value="#3498db", emoji="🔵"),
                           discord.SelectOption(label="緑", value="#2ecc71", emoji="🟢"),
                           discord.SelectOption(label="赤", value="#e74c3c", emoji="🔴"),
                           discord.SelectOption(label="黄", value="#f1c40f", emoji="🟡"),
                           discord.SelectOption(label="紫", value="#9b59b6", emoji="🟣"),
                           discord.SelectOption(label="黒", value="#23272a", emoji="⚫"),
                           discord.SelectOption(label="白", value="#ffffff", emoji="⚪"),
                       ])
    async def set_color(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild_id = interaction.guild_id
        storage.set_guild_data(guild_id, "embed_color", select.values[0])
        await interaction.response.send_message(f"Embedの色を {select.values[0]} に設定しました。", ephemeral=True)

    @discord.ui.button(label="タイムスタンプON/OFF", style=discord.ButtonStyle.secondary, custom_id="embed_toggle_timestamp")
    async def toggle_timestamp(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        current_status = storage.get_setting(guild_id, "embed_timestamp", False)
        new_status = not current_status
        storage.set_guild_data(guild_id, "embed_timestamp", new_status)
        status_text = "ON" if new_status else "OFF"
        await interaction.response.send_message(f"タイムスタンプを {status_text} に設定しました。", ephemeral=True)

    @discord.ui.button(label="ボタン設定", style=discord.ButtonStyle.primary, custom_id="embed_manage_buttons")
    async def manage_buttons(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Embedに付与するボタンを管理します。", view=EmbedButtonManageView(), ephemeral=True)

    @discord.ui.button(label="プレビュー", style=discord.ButtonStyle.secondary, custom_id="embed_preview")
    async def preview_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        embed = await self._get_current_embed(guild_id)
        
        buttons_data = storage.get_setting(guild_id, "embed_buttons", [])
        preview_view = discord.ui.View(timeout=60)
        if buttons_data:
            for btn_data in buttons_data:
                preview_view.add_item(EmbedLinkButton(label=btn_data["label"], url=btn_data["url"]))

        await interaction.response.send_message("現在のEmbedのプレビューです。", embed=embed, view=preview_view if buttons_data else None, ephemeral=True)

    @discord.ui.channel_select(placeholder="Embedを送信するチャンネルを選択", custom_id="embed_send_channel")
    async def send_channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        guild_id = interaction.guild_id
        channel = select.values[0]
        
        if not isinstance(channel, discord.TextChannel):
            return await interaction.response.send_message("テキストチャンネルを選択してください。", ephemeral=True)

        embed = await self._get_current_embed(guild_id)
        buttons_data = storage.get_setting(guild_id, "embed_buttons", [])
        
        final_view = discord.ui.View(timeout=None) # 永続View
        if buttons_data:
            for btn_data in buttons_data:
                final_view.add_item(EmbedLinkButton(label=btn_data["label"], url=btn_data["url"]))

        try:
            message = await channel.send(embed=embed, view=final_view if buttons_data else None)
            # 永続ViewのためにメッセージIDとチャンネルIDを保存
            if buttons_data:
                storage.set_guild_data(guild_id, f"embed_message_{message.id}", {
                    "channel_id": channel.id,
                    "buttons": buttons_data
                })
            await interaction.response.send_message(f"Embedを {channel.mention} に送信しました！", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Botにこのチャンネルへのメッセージ送信権限がありません。", ephemeral=True)

class EmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed-setup", description="Embed作成パネルのセットアップを開始します")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed_setup(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Embed作成システム",
            description="以下のボタンやメニューを使用して、カスタムEmbedを作成してください。\n設定完了後、チャンネルを選択して送信してください。",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=EmbedSetupView(), ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        # Bot起動時に永続Viewを登録
        # Embedにボタンが設定されている場合のみPersistentViewを登録
        for guild_id_str in storage.data:
            guild_id = int(guild_id_str)
            guild_data = storage.get_guild_data(guild_id)
            for key, value in guild_data.items():
                if key.startswith("embed_message_") and "buttons" in value:
                    message_id = int(key.replace("embed_message_", ""))
                    channel_id = value["channel_id"]
                    buttons_data = value["buttons"]

                    view = discord.ui.View(timeout=None)
                    for btn_data in buttons_data:
                        view.add_item(EmbedLinkButton(label=btn_data["label"], url=btn_data["url"]))
                    
                    self.bot.add_view(view)
                    print(f"Registered persistent embed view for message {message_id} in guild {guild_id}")

        print("Embed Cog is ready and Persistent Views added.")

async def setup(bot):
    await bot.add_cog(EmbedCog(bot))
