import discord
from discord import app_commands
from discord.ext import commands

id_do_servidor = "1058104550734712933"
id_cargo_atendente = "1058217906745376798"
token_bot ="MTA1ODIzODUyMTIwODQ4Nzk0Ng.GpcNJ4.3Qrc3SSM7D0u7mnIjKp8ePe7616A6xXs2iqgkg"


class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(value="ajuda",label="Fazer uma Denuncia"),
            discord.SelectOption(value="duvidas",label="Tirar-Duvidas"),
        ]
        super().__init__(
            placeholder="Selecione uma opção...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:dropdown_help"
        )
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "ajuda":
            await interaction.response.send_message("Clique abaixo para criar um denuncia.",ephemeral=True, view=CreateTicket())
        elif self.values[0] == "duvidas":
            await interaction.response.send_message("Clique abaixo para tirar suas duvidas.",ephemeral=True,view=CreateTicket()) 


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Dropdown())

class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value=None

    @discord.ui.button(label="Abrir Ticket",style=discord.ButtonStyle.blurple,emoji="➕")
    async def confirm(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(ephemeral=True,content=f"Você já tem um atendimento em andamento!")
                    return
        
        if ticket != None:
            await ticket.unarchive()
            await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})",auto_archive_duration=10080,invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})",auto_archive_duration=10080)#,type=discord.ChannelType.public_thread)
            await ticket.edit(invitable=False)

            await interaction.response.send_message(ephemeral=True,content=f"Criei um ticket para você! {ticket.mention}")
            await ticket.send(f"<@&1058217906745376798> {interaction.user.mention}  Ticket criado!, Informe oque deseja, nossa equipe ira te responder.")


class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False #Nós usamos isso para o bot não sincronizar os comandos mais de uma vez

    async def setup_hook(self) -> None:
        self.add_view(DropdownView())

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: #Checar se os comandos slash foram sincronizados 
            await tree.sync(guild = discord.Object(id=id_do_servidor)) # Você também pode deixar o id do servidor em branco para aplicar em todos servidores, mas isso fará com que demore de 1~24 horas para funcionar.
            self.synced = True
        print(f"Entramos como {self.user}.") 

aclient = client()

tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=id_do_servidor), name = 'setup', description='Setup')
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message(view=DropdownView()) 




@tree.command(guild = discord.Object(id=id_do_servidor), name="fecharticket",description='Feche um atendimento atual.')
async def _fecharticket(interaction: discord.Interaction):
    mod = interaction.guild.get_role(id_cargo_atendente)
    if str(interaction.user.id) in interaction.channel.name or mod in interaction.author.roles:
        await interaction.response.send_message(f"O ticket foi arquivado por {interaction.user.mention}, obrigado por entrar em contato!")
        await interaction.channel.edit(archived=True)
    else:
        await interaction.response.send_message("Isso não pode ser feito aqui...")

aclient.run(token_bot)
