import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
from math import log
from ttkthemes import ThemedStyle


def simple_lemmatize(word):
    # Basic French lemmatization rules
    lemmatized_word = word.lower()  # For simplicity, converting to lowercase

    # Rules for French lemmatization
    if lemmatized_word.endswith(('s', 'x', 'é')):
        lemmatized_word = lemmatized_word[:-1]

    if lemmatized_word.endswith(('es', 'ez')):
        lemmatized_word = lemmatized_word[:-2]

    if lemmatized_word.endswith(('ant', 'ants', 'ité', 'ités', 'ies')):
        lemmatized_word = lemmatized_word[:-3]

    if lemmatized_word.endswith(('ion', 'ité', 'ités')):
        lemmatized_word = lemmatized_word[:-3]

    if lemmatized_word.endswith(('amment', 'emment', 'issement')):
        lemmatized_word = lemmatized_word[:-6]

    if lemmatized_word.endswith(('ir', 'is', 'it', 'ie')):
        lemmatized_word = lemmatized_word[:-2]

    if lemmatized_word.endswith(('ions', 'tion', 'sion', 'ants', 'eurs', 'euse', 'ants')):
        lemmatized_word = lemmatized_word[:-4]

    if lemmatized_word.endswith(('eur', 'eurs', 'eus')):
        lemmatized_word = lemmatized_word[:-3]

    if lemmatized_word.endswith(('ique', 'ques')):
        lemmatized_word = lemmatized_word[:-4]

    if lemmatized_word.endswith(('iste', 'istes', 'isme', 'ismes')):
        lemmatized_word = lemmatized_word[:-3]

    if lemmatized_word.startswith(('dé', 're', 'pré', 'sur', 'sous', 'contre', 'entre', 'extra')):
        lemmatized_word = lemmatized_word[2:]

    if lemmatized_word.startswith(('dé', 're')):
        lemmatized_word = lemmatized_word[2:]

    if lemmatized_word.startswith(('pré', 'sur')):
        lemmatized_word = lemmatized_word[3:]

    if lemmatized_word.startswith(('sous',)):
        lemmatized_word = lemmatized_word[4:]

    if lemmatized_word.startswith(('entre', 'extra')):
        lemmatized_word = lemmatized_word[5:]

    if lemmatized_word.startswith(('contre',)):
        lemmatized_word = lemmatized_word[6:]

    return lemmatized_word



class TextPreprocessingApp:
    def __init__(self, master):
        self.master = master
        master.title("Text Preprocessing GUI")

        self.corpus_file_path = ""
        self.stop_words_file_path = ""

        # Apply the ThemedStyle for a modern look
        self.style = ThemedStyle(master)
        self.style.set_theme("plastik")

        self.tab_control = ttk.Notebook(master)

        self.preprocess_tab = tk.Frame(self.tab_control, background="#F0F0F0")
        self.tab_control.add(self.preprocess_tab, text="Preprocess Corpus")

        self.corpus_label = tk.Label(self.preprocess_tab, text="Select Corpus File:", font=("Arial", 12),
                                     background="#F0F0F0")
        self.corpus_label.pack()

        self.corpus_button = ttk.Button(self.preprocess_tab, text="Choose Corpus", command=self.choose_corpus_file)
        self.corpus_button.pack()

        self.stop_words_label = tk.Label(self.preprocess_tab, text="Select Stop Words File:", font=("Arial", 12),
                                         background="#F0F0F0")
        self.stop_words_label.pack()

        self.stop_words_button = ttk.Button(self.preprocess_tab, text="Choose Stop Words",
                                            command=self.choose_stop_words_file)
        self.stop_words_button.pack()

        self.num_documents_label = tk.Label(self.preprocess_tab, text="Number of Documents:", font=("Arial", 12),
                                            background="#F0F0F0")
        self.num_documents_label.pack()

        self.num_documents_entry = tk.Entry(self.preprocess_tab, font=("Arial", 12))
        self.num_documents_entry.pack()

        self.start_button = ttk.Button(self.preprocess_tab, text="Start Preprocessing",
                                       command=self.start_preprocessing)
        self.start_button.pack()

        self.results_text = tk.Text(self.preprocess_tab, height=10, width=50, font=("Arial", 10), wrap="word")

        # Adding scrollbar to the text widget
        scrollbar = tk.Scrollbar(self.preprocess_tab, command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")

        self.results_text.config(yscrollcommand=scrollbar.set)
        self.results_text.pack(side="left", fill="both", expand=True)

        self.search_tab = tk.Frame(self.tab_control, background="#F0F0F0")
        self.tab_control.add(self.search_tab, text="Search Documents")

        self.search_word_label = tk.Label(self.search_tab, text="Search Word:", font=("Arial", 12),
                                          background="#F0F0F0")
        self.search_word_label.pack()

        self.search_word_entry = tk.Entry(self.search_tab, font=("Arial", 12))
        self.search_word_entry.pack()

        self.search_button = ttk.Button(self.search_tab, text="Search", command=self.search_documents)
        self.search_button.pack()

        self.results_text_search = tk.Text(self.search_tab, height=10, width=50, font=("Arial", 10), wrap="word")

        # Adding scrollbar to the text widget
        scrollbar_search = tk.Scrollbar(self.search_tab, command=self.results_text_search.yview)
        scrollbar_search.pack(side="right", fill="y")

        self.results_text_search.config(yscrollcommand=scrollbar_search.set)
        self.results_text_search.pack(side="left", fill="both", expand=True)

        self.tab_control.pack(expand=1, fill="both")

    def choose_corpus_file(self):
        self.corpus_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.corpus_label.config(text=f"Selected Corpus: {os.path.basename(self.corpus_file_path)}")

    def choose_stop_words_file(self):
        self.stop_words_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.stop_words_label.config(text=f"Selected Stop Words: {os.path.basename(self.stop_words_file_path)}")

    def start_preprocessing(self):
        num_documents = int(self.num_documents_entry.get())
        if not self.corpus_file_path or not self.stop_words_file_path or num_documents <= 0:
            messagebox.showerror("Error", "Please select valid inputs.")
            return

        index = self.preprocess_corpus(self.corpus_file_path, self.stop_words_file_path, num_documents)

        self.results_text.delete(1.0, tk.END)
        for term, positions in index.items():
            self.results_text.insert(tk.END, f'{term}: {", ".join(positions)}\n')

    def preprocess_corpus(self, corpus_file, stop_words_file, num_documents):
        text_corpus = self.read_file(corpus_file)
        stop_words = self.read_stop_words(stop_words_file)

        documents = self.split_into_documents(text_corpus, num_documents)
        index = defaultdict(list)

        for i, doc in enumerate(documents, 1):
            preprocessed_doc, term_info = self.preprocess_text(doc, stop_words, i)
            self.save_documents_to_folder([preprocessed_doc], 'preprocessed_documents')

            for term, positions in term_info.items():
                index[term].extend([f'{pos[0]}({pos[1]})' for pos in positions])

        return index

    def read_file(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()

    def read_stop_words(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            stop_words = file.read().splitlines()
        return set(stop_words)

    def split_into_documents(self, text, num_documents):
        total_length = len(text)
        documents = []
        document_size = total_length // num_documents

        for i in range(num_documents):
            start_index = i * document_size
            end_index = (i + 1) * document_size
            document = text[start_index:end_index]
            documents.append(document)

        return documents

    def preprocess_text(self, text, stop_words, doc_num):
        text = re.sub(r'[^\w\s]', '', text)
        text = text.lower()
        words = text.split()
        words = [word for word in words if word not in stop_words]

        lemmatized_words = [simple_lemmatize(word) for word in words]

        term_info = defaultdict(list)
        preprocessed_text = []
        for idx, word in enumerate(lemmatized_words, start=1):
            term_info[word].append((doc_num, idx))
            preprocessed_text.append(f'{word}(DOC_{doc_num},{idx})')

        return ' '.join(preprocessed_text), term_info

    def save_documents_to_folder(self, documents, folder_path):
        os.makedirs(folder_path, exist_ok=True)

        for i, document in enumerate(documents, 1):
            file_name = f'DOC_{i}.txt'
            file_path = os.path.join(folder_path, file_name)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(document)

    def search_documents(self):
        search_word = self.search_word_entry.get().lower()

        if not search_word:
            messagebox.showerror("Error", "Please enter a search word.")
            return

        tfidf_weights = self.calculate_tfidf(search_word)

        # Sort the documents based on TF-IDF weights
        sorted_documents = sorted(tfidf_weights.items(), key=lambda x: x[1], reverse=True)

        self.results_text_search.delete(1.0, tk.END)

        if not sorted_documents:
            self.results_text_search.insert(tk.END, "No matching documents.")
        else:
            # Display the sorted documents
            for doc_num, tfidf_weight in sorted_documents:
                self.results_text_search.insert(tk.END, f'DOC_{doc_num}: TF-IDF = {tfidf_weight:.4f}\n')

            # Check for similar TF-IDF weights
            similar_documents = [(doc_num, tfidf_weight) for doc_num, tfidf_weight in sorted_documents if tfidf_weight == sorted_documents[0][1]]

            if len(similar_documents) > 1:
                self.results_text_search.insert(tk.END, "\nSimilar documents:\n")
                for doc_num, tfidf_weight in similar_documents:
                    self.results_text_search.insert(tk.END, f'DOC_{doc_num}: TF-IDF = {tfidf_weight:.4f}\n')

    def calculate_tfidf(self, search_word):
        num_documents = int(self.num_documents_entry.get())
        tfidf_weights = defaultdict(float)
        document_frequencies = defaultdict(int)

        # Lemmatize the search word using your custom lemmatization function
        search_word_lemma = simple_lemmatize(search_word.lower())

        for doc_num in range(1, num_documents + 1):
            document_path = os.path.join('preprocessed_documents', f'DOC_{doc_num}.txt')
            with open(document_path, 'r', encoding='utf-8') as file:
                document_content = file.read()

            # Lemmatize the document content using your custom lemmatization function
            document_lemmas = [simple_lemmatize(word) for word in document_content.lower().split()]

            # Count the occurrences of the lemmatized search word in the document
            term_count = document_lemmas.count(search_word_lemma)
            total_terms = len(document_lemmas)
            tf = term_count / total_terms if total_terms > 0 else 0

            if term_count > 0:
                document_frequencies[search_word_lemma] += 1
            idf = log(num_documents / (1 + document_frequencies[search_word_lemma]))

            tfidf_weights[doc_num] = tf * idf

        return tfidf_weights


if __name__ == "__main__":
    root = tk.Tk()
    app = TextPreprocessingApp(root)
    root.mainloop()
