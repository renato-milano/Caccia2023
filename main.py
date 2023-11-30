import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters,ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHOOSING, FINDING,TYPING_REPLY,MOMENTO_FRASE ,TYPING_CHOICE,CHOOSING_LANG = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ciao, sono il bot di ricerca per la Caccia al tesoro 2023!")
    await context.bot.send_message(chat_id=update.effective_chat.id,text="in che lingua vuoi cercare?")
    return CHOOSING

async def scegliLibro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "in ing".lower() in update.message.text.lower():
        libri = selezionaLibro("in inglese")
        context.user_data["lingua"] = "ENG"
    else:
        libri = selezionaLibro("in italiano")
        context.user_data["lingua"] = "ITA"
    x=1
    context.user_data["TuttiLibri"] = {}
    risposta="Scegli il libro in cui cercare\n\n"
    for libro in libri:
        context.user_data["TuttiLibri"][str(x)] = libro
        risposta = risposta+str(x)+". "+libro.replace("-"," ").replace(".txt"," ")+"\n"
        x=x+1
    risposta = risposta+"\nPuoi selezionare più libri separati dalla virgola, ad esempio '1,2,3,4...'\n Oppure rispondi con 'tutti'"
    await update.message.reply_text(risposta)
    print(context.user_data["TuttiLibri"])

    return MOMENTO_FRASE

async def inserimentoFrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messagg = update.message.text
    numLiB = messagg.split(",")
    risp=""
    if messagg.lower()!="tutti":
    
        context.user_data["libri"]=[]
        for num in numLiB:
            context.user_data["libri"].append(context.user_data["TuttiLibri"][num])
    else:
        context.user_data["libri"]=[]
        for chiave,valore in context.user_data["TuttiLibri"].items():
            context.user_data["libri"].append(valore)

    for libri in context.user_data["libri"]:
        risp= risp+libri+"\n"

    await context.bot.send_message(chat_id=update.effective_chat.id,text="Libri slezionati:\n"+risp)
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Cosa vuoi cercare?")
    return TYPING_CHOICE


async def messaggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    frase = update.message.text
    testo = cerca(context,context.user_data["libri"])
    testi = context.user_data["libri_divisi"]
    parte_del_contenuto = "Non trovato"
    if frase in testo:
        inizio = testo.index(frase)
        fine = inizio + len(frase)
        parte_del_contenuto = testo[inizio-500: fine+500]
        if parte_del_contenuto=="":
            parte_del_contenuto= testo[inizio: fine+1000]

    #await update.message.reply_text(parte_del_contenuto)
    for chiave,valore in testi.items():
        if frase in valore:
            inizio = valore.index(frase)
            fine = inizio + len(frase)
            parte_del_contenuto = valore[inizio-500: fine+500]
            if parte_del_contenuto=="":
                parte_del_contenuto= valore[inizio: fine+1000]
            
            await update.message.reply_text("Dal File: "+ chiave+"\n\n Pezzo Estratto:\n\n"+parte_del_contenuto)
    
    await update.message.reply_text("Vuoi cercare altro? in che lingua?")
    return CHOOSING



def libroSpecifico(context,scelta):
    if  context.user_data["lingua"] ==1:
        cartella = "testi"
    else: 
        cartella= "testi_ininglese"
    titolo = context.user_data["libri"][scelta]


def cerca(context,libri):
    contenuto_totale = ""
    libri_divisi = {}
    if context.user_data["lingua"] == "ITA":
        cartella = "testi"
    else:
        cartella = "testi_inglese"
    # Verifica se la cartella esiste
    if not os.path.exists(cartella):
        print(f"La cartella '{cartella}' non esiste.")
        return contenuto_totale
    
    # Elenco dei file nella cartella
    file_nella_cartella = os.listdir(cartella)
    # Loop attraverso i file e leggi il contenuto dei file di testo
    for file in file_nella_cartella:
        if file in libri:
            percorso_file = os.path.join(cartella, file)
        
            # Verifica se il percorso è un file di testo
            if os.path.isfile(percorso_file) and file.endswith('.txt'):
                with open(percorso_file, 'r', encoding='utf-8') as f:
                    contenuto_file = f.read()
                    contenuto_totale += contenuto_file + "\n"  # Aggiungi una riga vuota tra i contenuti dei file
            libri_divisi[percorso_file] = contenuto_file
    context.user_data["libri_divisi"] = libri_divisi
    return contenuto_totale.lower()



def cercaItaliano():
    contenuto_totale = ""
    cartella = "testi"
    # Verifica se la cartella esiste
    if not os.path.exists(cartella):
        print(f"La cartella '{cartella}' non esiste.")
        return contenuto_totale
    
    # Elenco dei file nella cartella
    file_nella_cartella = os.listdir(cartella)
    
    # Loop attraverso i file e leggi il contenuto dei file di testo
    for file in file_nella_cartella:
        percorso_file = os.path.join(cartella, file)
        
        # Verifica se il percorso è un file di testo
        if os.path.isfile(percorso_file) and file.endswith('.txt'):
            with open(percorso_file, 'r', encoding='utf-8') as f:
                contenuto_file = f.read()
                contenuto_totale += contenuto_file + "\n"  # Aggiungi una riga vuota tra i contenuti dei file
    
    return contenuto_totale

def selezionaLibro(messaggio):
    if "in inglese" in messaggio:
        cartella= "testi_inglese"
    else:
        cartella= "testi"
    if not os.path.exists(cartella):
        print(f"La cartella '{cartella}' non esiste.")
        return []

    # Elenco dei file nella cartella
    file_nella_cartella = os.listdir(cartella)

    # Filtra solo i file (escludendo le cartelle)
    file_nella_cartella = [file for file in file_nella_cartella if os.path.isfile(os.path.join(cartella, file))]
    print(file_nella_cartella)
    return file_nella_cartella


def cercaInglese():
    contenuto_totale = ""
    cartella = "testi_inglese"
    # Verifica se la cartella esiste
    if not os.path.exists(cartella):
        print(f"La cartella '{cartella}' non esiste.")
        return contenuto_totale
    
    # Elenco dei file nella cartella
    file_nella_cartella = os.listdir(cartella)
    
    # Loop attraverso i file e leggi il contenuto dei file di testo
    for file in file_nella_cartella:
        percorso_file = os.path.join(cartella, file)
        
        # Verifica se il percorso è un file di testo
        if os.path.isfile(percorso_file) and file.endswith('.txt'):
            with open(percorso_file, 'r', encoding='utf-8') as f:
                contenuto_file = f.read()
                contenuto_totale += contenuto_file + "\n"  # Aggiungi una riga vuota tra i contenuti dei file
    
    return contenuto_totale
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text("FINE")

    user_data.clear()
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token('6588143546:AAGiu4ltm3ew7gRRTHEKosOzrioAESie_oM').build()
    
    #start_handler = CommandHandler('start', start)
    #message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), messaggio)
    #message_handler = MessageHandler(filters.TEXT  & (~filters.COMMAND) & filters.Regex("^Cerca$"), messaggio)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
         
            CHOOSING: [
                MessageHandler(
                    filters.TEXT , scegliLibro
                )
            ],
               MOMENTO_FRASE: [
                MessageHandler(
                    filters.TEXT , inserimentoFrase
                )
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT , messaggio
                )
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)