# importing modules
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import re
from functools import reduce
from tkinter import *

ps = PorterStemmer()


class Boolean_Model:
    inverted_index = {}
    positional_index = {}
    stop_words = []

    def __init__(self):
        self.create_inverted_index()
        self.create_positional_index()
        sw = open("E:/STUDY/IR/A1/mark1/Stopword-List.txt")
        for stop in sw:
            stop = re.sub('[^A-Za-z]+', '', stop)
            self.stop_words.append(stop)
        sw.close()

    def create_inverted_index(self):
        file_name = "1"

        for _ in range(448):
            # reading from file
            with open("E:/STUDY/IR/A1/mark1/Abstracts/" + file_name + ".txt") as f:
                z = f.read()

            # filtering
            z = re.sub('[^A-Za-z]+', ' ', z)

            # converting to lowercase
            z = z.lower()

            # tokens
            words = word_tokenize(z)

            # removing similar words
            words = list(set(words))

            # creating inverted index and removing stop words
            for w in words:
                if w not in self.stop_words:
                    w = ps.stem(w)
                    if w in self.inverted_index:
                        if not isinstance(self.inverted_index[w], list):
                            self.inverted_index[w] = [self.inverted_index[w]]
                        self.inverted_index[w].append(int(file_name))
                        self.inverted_index[w] = list(set(self.inverted_index[w]))
                        self.inverted_index[w].sort()
                    else:
                        self.inverted_index[w] = int(file_name)

            file_name = str(int(file_name) + 1)
            words.clear()

        fw = open("inverted index.txt", 'w')
        zk = open("checking.txt", "w")
        for key in sorted(self.inverted_index):
            index = (key + '->' + str(self.inverted_index[key]) + '\n')
            # print(index)
            # print(key)
            fw.write(index)
            zk.write(key+'\n')
        fw.close()
        zk.close()

    def create_positional_index(self):
        for file_name in range(1, 449):
            # reading the file
            with open("E:/STUDY/IR/A1/mark1/Abstracts/" + str(file_name) + ".txt") as f:
                z = f.read()

            # cleaning of words
            z = z.lower()
            z = re.sub('[^A-Za-z1-9]+', ' ', z)
            z = z.split()

            # creating positional index
            position = 1
            for word in z:
                word = ps.stem(word)
                if not word.isnumeric() and word not in self.stop_words and len(word) > 1:
                    if word not in self.positional_index:
                        temp_dic = {}
                        temp_lis = [position]
                        position += 1
                        temp_dic[file_name] = temp_lis
                        self.positional_index[word] = temp_dic
                    elif word in self.positional_index:
                        if file_name not in self.positional_index[word]:
                            temp_lis = [position]
                            position += 1
                            self.positional_index[word][file_name] = temp_lis
                        elif file_name in self.positional_index[word]:
                            self.positional_index[word][file_name].append(position)
                            position += 1
                else:
                    position += 1

        # writing positional index in file
        fw = open("positional index.txt", 'w')
        for key in sorted(self.positional_index):
            index = (key + '->' + str(self.positional_index[key]) + '\n')
            fw.write(index)
        fw.close()

    def action_search_proximity_query(self, query):
        # first, create positional index
        #self.create_positional_index()

        # splitting the query
        query = query.split()

        # making dictionary for filtered words
        filtered_indexes = {}

        # final list for our output
        final = []

        for i in range(0, len(query)):
            if "/" in query[i]:
                # getting words on which have to do lookup
                words = [ps.stem(query[i - 2]), ps.stem(query[i - 1])]
                filtered_indexes[ps.stem(query[i-2])] = self.positional_index[ps.stem(query[i-2])]
                filtered_indexes[ps.stem(query[i-1])] = self.positional_index[ps.stem(query[i-1])]
                k = re.sub('[^A-Za-z1-9]+', ' ', query[i])
                k = int(k)
                for key1 in filtered_indexes[words[0]]:                     # getting document number of first word
                    for key2 in filtered_indexes[words[1]]:                 # getting document number of first word
                        if key1 == key2:                                    # check if both words are in same documents
                            for pos1 in filtered_indexes[words[0]][key1]:
                                for pos2 in filtered_indexes[words[1]][key1]:
                                    # check if both words are k terms apart
                                    #if ((int(pos1)+k+1) == int(pos2)) or ((int(pos2)+k+1) == int(pos1)):
                                    if abs(int(pos1) - int(pos2)) <= k+1:
                                        final.append(key1)
                words.clear()

        final = list(set(final))
        final.sort()
        # print("Output is:", str(final))
        return final

    def query_check(self,query):
        # query
        #query = input("Enter query: ")
        if "AND" in query or "OR" in query or "NOT" in query:
            return self.action_search_inverted_index(query)
        elif "/" in query:
            return self.action_search_proximity_query(query)
        else:
            return self.action_search_inverted_index(query)

    def action_search_inverted_index(self, query):
        lookup = []
        filtered_indexes = {}
        final_docs = []
        operations = 0

        # splitting query making tokens
        query = query.split(' ')
        #print(query)
        # stemming query
        for gh in range(0, len(query)):
            if (query[gh] != "AND") and (query[gh] != "OR") and (query[gh] != "NOT"):
                query[gh] = ps.stem(query[gh])

        # creating inverted index
        #self.create_inverted_index()

        # creating lookup array of words
        for words in query:
            if (words != "AND") and (words != "OR") and (words != "NOT"):
                words = ps.stem(words)
                lookup.append(words.lower())
            else:
                operations += 1

        # getting query words filtered getting their posting lists
        for i in range(0, len(lookup)):
            if lookup[i] in self.inverted_index.keys():
                filtered_indexes[lookup[i]] = self.inverted_index[lookup[i]]

        # query processing for NOT
        for i in range(0, len(query)):
            if query[i] == "NOT":
                if not isinstance(filtered_indexes[query[i+1]], list):
                    filtered_indexes[query[i+1]] = [filtered_indexes[query[i+1]]]
                for z in range(1, 449):
                    if z in filtered_indexes[query[i+1]]:
                        filtered_indexes[query[i+1]].remove(z)
                    else:
                        filtered_indexes[query[i+1]].append(z)
                filtered_indexes[query[i+1]].sort()

        # print(query)
        # print(lookup)
        # print(filtered_indexes)

        # final docs have the keys of filtered index i.e. the posting list of query words
        for key in filtered_indexes:
            final_docs.append(filtered_indexes[key])
        # print(final_docs)

        # doing OR AND operations the posting lists final_docs
        final = []
        # f_or = []
        if len(final_docs) > 1:
            for qr in range(0, len(query)):
                if qr == 0:
                    final.append(filtered_indexes[query[0]])
                elif query[qr] == "AND":
                    if query[qr+1] == "NOT":
                        final.append(filtered_indexes[query[qr+2]])
                        fk = list(reduce(lambda i, j: i & j, (set(x) for x in final)))
                        fk.sort()
                        final.clear()
                        if len(fk) > 0:
                            final.append(fk)
                    else:
                        final.append(filtered_indexes[query[qr + 1]])
                        fk = list(reduce(lambda i, j: i & j, (set(x) for x in final)))
                        fk.sort()
                        final.clear()
                        if len(fk) > 0:
                            final.append(fk)
                elif query[qr] == "OR":
                    f_or = final[0] + filtered_indexes[query[qr + 1]]
                    final.clear()
                    f_or = list(set(f_or))
                    f_or.sort()
                    final.append(f_or)
                elif query[qr] == "NOT":
                    final.append(filtered_indexes[query[qr + 1]])
        else:
            final = final_docs

        # sorting the final list
        final.sort()

        # print(final)
        return final


bm = Boolean_Model()

window = Tk()

window.title("Assignment-1")
window.minsize(width=1000,height=800)
window.config(padx=50)
canvas=Canvas(width=724,height=501,highlightthickness=0)
img=PhotoImage(file="simg-removebg-preview.png")
canvas.create_image(362,250, image=img)
my_label=Label(text="Enter Query: ",font=("Arial",24,"bold"))
my_label.place(relx=0.5,rely=0.6,anchor="center")
input1=Entry(width=50,font=("Arial",15))
input1.place(relx=0.5,rely=0.65,anchor="center")

def search():
    output.delete("1.0","end")
    output.insert(END,"Terms found in Documents:"+str(bm.query_check(input1.get())))


button=Button(text="Search",command=search,width=10,height=1)
button.place(relx=0.5,rely=0.7,anchor="center")
output=Text(height=7,width=50,font=("Arial",15))
output.insert(END,"")
output.place(relx=0.3,rely=0.75)

canvas.pack()
window.mainloop()
