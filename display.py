# Permet de récupérer les tokens d'un prompt
import tiktoken
# Permet de récupérer la date et l'heure
from datetime import datetime
# permet d'accéder à la sortie standart
import sys
# permet de créer des dossiers, changer les droits, supprimer des fichiers, etc
import os


class Display:
    """
    --------------------------------------------------------------------------------------------------------------
                                                Classe display
    --------------------------------------------------------------------------------------------------------------
    Description:
        Classe axée sur l'affichage et le interactions utilisateur
    --------------------------------------------------------------------------------------------------------------
    Méthodes accessibles:

        createLog(self)
            -> Permet de créer un fichier log.csv pour enregistrer les logs pour l'utilisation d'une API
        displayCost(self,prompt,system = "",user = True)
            -> affiche le coût d'une requête pour l'utilisation d'une API
        displayResult(self,result,function_name,previous_text = "",previous_input_size = 0,previous_output_size=0)
            -> affiche le résultat d'une requête pour l'utilisation d'une API
        longInput(self,text)
            ->Permet de faire un input sur plusieurs lignes. En sort avec Ctrl C
        
    --------------------------------------------------------------------------------------------------------------
    """
    def __init__(self) -> None:
        # Définit le modéle d'encodage en tokens
        self.enc = tiktoken.get_encoding("cl100k_base")
        self.enc = tiktoken.encoding_for_model("gpt-4")
        self.input_price = 0.00001
        self.output_price = 0.00003


    def createLog(self):
        #Permet de créer un fichier log.csv
        with open ('log.csv', 'w') as f:
            f.write('date;fonction;token input;token output;price')

    def displayCost(self,prompt,system = "",user = True):
        #Permet d'afficher le coût de la requête
        
        # affichage de la réponse à la requête
        if (not user):
            print(prompt)
    
        #permet de fonctionner aussi bien au début quand on rajoute un prompt system que pendant la conversation
        size = len(self.enc.encode(prompt))
        if system != "":
            size += len(self.enc.encode(system))

        print("\n\033[91m{} tokens ont été {}, coût: {}$\033[0m".format(size,'envoyés' if user else 'reçu', size*self.output_price))
        return size

    def displayAndSave(self,all_text,input_size,output_size,name):
        #écrit le résultat dans un fichier du même nom que la fonction
        with open ("results/"+name+'.txt', 'w') as f:
            f.write(all_text)

        # ecrit les données de log dans un fichier log.csv
        if not os.path.exists('log.csv'):
            self.createLog()
        
        with open ('log.csv', 'a') as f:
            f.write('\n{};{};{};{};{}'.format(datetime.now(),
                                            name,
                                            input_size,
                                            output_size,
                                            input_size*self.input_price+output_size*self.output_price))
            
    
    def displayResult(self,result,function_name,previous_text = "",previous_input_size = 0,previous_output_size=0):
        
        """
        Permet d'afficher le résultat de la requête

        les "previous" permettent de calculer le coût total de la requête et d'afficher l'entière discussion dans un fichier
        function_name permet de créer automatique un fichier du même nom que la fonction teste pour y écrire la discussion
        """ 

        #récupères les informations renvoyées par le test
        result_text, input_size = result

        #affichage du premier résultat et du coût
        response = result_text.choices[0].message.content
        output_size = self.displayCost(response, user=False)

        self.displayAndSave(all_text=previous_text+"\n"+response,
                            input_size=previous_input_size+ input_size,
                            output_size=previous_output_size+output_size,
                            name=function_name)

    def longInput(self,text):
        """
            Moins bien que promptAsk -> à remplacer
        """
        # List to store user inputs
        input_lines = ""

        print(text+"Appuyez 'Ctrl+C' pour valider: \n")

        try:
            while True:
                line = input(">>")
                input_lines+=line+"\n"

        except KeyboardInterrupt:
            print("\nExiting input...\n")

            return input_lines

    
    