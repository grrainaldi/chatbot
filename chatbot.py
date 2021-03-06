# PA6, CS124, Stanford, Winter 2019
# v.1.0.3
# Original Python code by Ignacio Cases (@cases)
######################################################################
import movielens
import sys
import os
import re
import math

import numpy as np
from nltk.tokenize import word_tokenize
from PorterStemmer import PorterStemmer

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
      # The chatbot's default name is `moviebot`. Give your chatbot a new name.
      self.name = 'Lit!'

      self.creative = creative

      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, ratings = movielens.ratings()

      self.sentiment = {}
      self.porter_stemmer = PorterStemmer()
      sentimentCopy = movielens.sentiment()

      for k, v in sentimentCopy.items():
        key = self.porter_stemmer.stem(k)
        self.sentiment[key] = v


      self.user_ratings = []
      #############################################################################
      # TODO: Binarize the movie ratings matrix.                                  #
      #############################################################################
      ratings = self.binarize(ratings)
      # Binarize the movie ratings before storing the binarized matrix.
      self.ratings = ratings
      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

    #############################################################################
    # 1. WARM UP REPL                                                           #
    #############################################################################

    def greeting(self):
      """Return a message that the chatbot uses to greet the user."""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = "Hey there! I am your movie chatbot here to help recommend a movie to you. First, tell me about a movie you have seen and whether or not you liked it."

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return greeting_message

    def goodbye(self):
      """Return a message that the chatbot uses to bid farewell to the user."""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = "Thank you! I hope you enjoy your film!"

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return goodbye_message


    ###############################################################################
    # 2. Modules 2 and 3: extraction and transformation                           #
    ###############################################################################

    def process(self, line):
      """Process a line of input from the REPL and generate a response.

      This is the method that is called by the REPL loop directly with user input.

      You should delegate most of the work of processing the user's input to
      the helper functions you write later in this class.

      Takes the input string from the REPL and call delegated functions that
        1) extract the relevant information, and
        2) transform the information into a response to the user.

      Example:
        resp = chatbot.process('I loved "The Notebok" so much!!')
        print(resp) // prints 'So you loved "The Notebook", huh?'

      :param line: a user-supplied line of text
      :returns: a string containing the chatbot's response to the user input
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method,         #
      # possibly calling other functions. Although modular code is not graded,    #
      # it is highly recommended.                                                 #
      #############################################################################
      if self.creative:

        titles = self.extract_titles(line)
        if len(titles) > 1:
          return "Please tell me about only one movie at a time. Go ahead."

        sentiment = self.extract_sentiment(line)

        movies = []
        for i in titles:
          #FOR CREATIVE: CHANGE THIS TO DISAMBIGUATE BETWEEN TITLES BY USING BELOW CALL to start:
          #movies = self.find_movies_by_title(i)
          id_list = self.find_movies_closest_to_title(i)          
          if id_list == []:return "I'm sorry, I don't recognize that movie. Please enter in a different title."
          print("Found the following movies: " + str(id_list))
          #for simple mode: no disambiguate, just choose first id!
          movies = (self.find_movies_closest_to_title(i)[0], sentiment)        
          self.user_ratings.append(movies)
            
        
        if len(self.user_ratings) >= 5:
          suggestions = self.recommend(self.user_ratings, self.ratings)
          print(suggestions)

        response = "I processed {} in creative mode!!".format(self.user_ratings)

       
      else:

        titles = self.extract_titles(line)
        if len(titles) > 1:
          return "Please tell me about only one movie at a time. Go ahead."

        sentiment = self.extract_sentiment(line)

        movies = []
        for i in titles:
          #FOR CREATIVE: CHANGE THIS TO DISAMBIGUATE BETWEEN TITLES BY USING BELOW CALL to start:
          #movies = self.find_movies_by_title(i)
          id_list = self.find_movies_by_title(i)
          if id_list == []:return "I'm sorry, I don't recognize that movie. Please enter in a different title."
            #for simple mode: no disambiguate, just choose first id!
          movies = (self.find_movies_by_title(i)[0], sentiment)        
          self.user_ratings.append(movies)
            
        
        if len(self.user_ratings) >= 5:
          suggestions = self.recommend(self.user_ratings, self.ratings)
          print(suggestions)

        response = "I processed {} in starter mode!!".format(self.user_ratings)

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return response

    def extract_titles(self, text):
      """Extract potential movie titles from a line of text.

      Given an input text, this method should return a list of movie titles
      that are potentially in the text.

      - If there are no movie titles in the text, return an empty list.
      - If there is exactly one movie title in the text, return a list
      containing just that one movie title.
      - If there are multiple movie titles in the text, return a list
      of all movie titles you've extracted from the text.

      Example:
        potential_titles = chatbot.extract_titles('I liked "The Notebook" a lot.')
        print(potential_titles) // prints ["The Notebook"]
      
      :param text: a user-supplied line of text that may contain movie titles
      :returns: list of movie titles that are potentially in the text
      """
      #pattern regular = '[\"\'].+[\"\']'
      titles = re.findall('"([^"]*)"', text)
      return titles

    def process_title(self, title): 
      title = title.lower()
      word_list = title.split()
      if (word_list[0] == 'and' or word_list[0] == 'the' or word_list[0] == 'a'):
        word_list[-1] = word_list[-1] + ','
        word_list.append(word_list[0])
        word_list.pop(0)

      title = " ".join(word_list)
      return title

    def find_movies_by_title(self, title):
      """ Given a movie title, return a list of indices of matching movies.

      - If no movies are found that match the given title, return an empty list.
      - If multiple movies are found that match the given title, return a list
      containing all of the indices of these matching movies.
      - If exactly one movie is found that matches the given title, return a list
      that contains the index of that matching movie.

      Example:
        ids = chatbot.find_movies_by_title('Titanic')
        print(ids) // prints [1359, 1953]

      :param title: a string containing a movie title
      :returns: a list of indices of matching movies
      """
      title = self.process_title(title)

      id_list = []
      movie_list = movielens.titles()
      for i in range(len(movie_list)):
        if title in movie_list[i][0].lower():
          id_list.append(i)
      return id_list


    def extract_sentiment(self, text):
      """Extract a sentiment rating from a line of text.

      You should return -1 if the sentiment of the text is negative, 0 if the
      sentiment of the text is neutral (no sentiment detected), or +1 if the
      sentiment of the text is positive.

      As an optional creative extension, return -2 if the sentiment of the text
      is super negative and +2 if the sentiment of the text is super positive.

      Example:
        sentiment = chatbot.extract_sentiment('I liked "The Titanic"')
        print(sentiment) // prints 1

      :param text: a user-supplied line of text
      :returns: a numerical value for the sentiment of the text
      """

      neg_words = ["n't", "not", "no", "never"]
      punctuation = [".", ",", "!", "?", ";"]

      title = self.extract_titles(text) #remove title so its not included in sentiment
      if len(title) > 0: text = text.replace(title[0], "")

      tokens = re.findall(r"[\w']+|[.,!?;]", text)
      words = []
      for t in tokens:
        words = words + word_tokenize(t)

      pos_count = 0
      neg_count = 0
      i = 0
      while i < len(words):
        w = self.porter_stemmer.stem(words[i])
        if w in neg_words and i != len(words)-1: #Take opposite meaning of all words after
          
          j = i+1
          wordToNegate = self.porter_stemmer.stem(words[j])
          while wordToNegate not in punctuation and j < len(words):
            if wordToNegate in self.sentiment:
              if self.sentiment[wordToNegate] == "pos":
                neg_count += 1
              else:
                pos_count += 1
            j = j+1
            if j <= (len(words)-1): wordToNegate = self.porter_stemmer.stem(words[j])
          i = j #Jump ahead

        else: #find straight sentiment of words
          if w in self.sentiment:
            if self.sentiment[w] == "pos":
              pos_count += 1
            else:
              neg_count += 1
          i = i+1
        

      if pos_count > neg_count:
        return 1
      elif neg_count > pos_count:
        return -1
      else:
        return 0

    def extract_sentiment_for_movies(self, text):
      """Creative Feature: Extracts the sentiments from a line of text
      that may contain multiple movies. Note that the sentiments toward
      the movies may be different.

      You should use the same sentiment values as extract_sentiment, described above.
      Hint: feel free to call previously defined functions to implement this.

      Example:
        sentiments = chatbot.extract_sentiment_for_text('I liked both "Titanic (1997)" and "Ex Machina".')
        print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

      :param text: a user-supplied line of text
      :returns: a list of tuples, where the first item in the tuple is a movie title,
        and the second is the sentiment in the text toward that movie
      """
      pass

    # def edit_distance(self, movie1, movie2, len1, len2):
    #   if len1 == 0:
    #     return len2
    #   if len2 == 0:
    #     return len1

    #   if movie1[len1-1] == movie2[len2-1]:
    #     return self.edit_distance(movie1, movie2, len1-1, len2-1)

    #   try1 = 1 + self.edit_distance(movie1, movie2, len1, len2-1)
    #   try2 = 1 + self.edit_distance(movie1, movie2, len1-1, len2)
    #   try3 = 1 + self.edit_distance(movie1, movie2, len1-1, len2-1)
    #   # print(movie1)
    #   # print(movie2)
    #   # print(len1)
    #   # print(len2)
    #   return min(try1, try2, try3)

    def edit_distance(self, movie1, movie2, max_distance):
      rows = len(movie1) + 1
      cols = len(movie2) + 1
      grid = [[0 for col in range(cols)] for row in range(rows)]

      for row in range(1, rows):
        grid[row][0] = row
      
      for col in range(1, cols):
        grid[0][col] = col
      
      for col in range(1, cols):
        for row in range(1, rows):
          cost = 2
          if movie1[row-1] == movie2[col-1]:
            cost = 0
          deletion = 1 + grid[row-1][col]
          insertion = 1 + grid[row][col-1]
          sub = cost + grid[row-1][col-1]
          grid[row][col] = min(deletion, insertion, sub)
          # if grid[row][col] > max_distance:
          #   return -1
      #print(grid)
      return grid[row][col]



    def find_movies_closest_to_title(self, title, max_distance=3):
      """Creative Feature: Given a potentially misspelled movie title,
      return a list of the movies in the dataset whose titles have the least edit distance
      from the provided title, and with edit distance at most max_distance.

      - If no movies have titles within max_distance of the provided title, return an empty list.
      - Otherwise, if there's a movie closer in edit distance to the given title 
        than all other movies, return a 1-element list containing its index.
      - If there is a tie for closest movie, return a list with the indices of all movies
        tying for minimum edit distance to the given movie.

      Example:
        chatbot.find_movies_closest_to_title("Sleeping Beaty") # should return [1656]

      :param title: a potentially misspelled title
      :param max_distance: the maximum edit distance to search for
      :returns: a list of movie indices with titles closest to the given title and within edit distance max_distance
      """

      title = self.process_title(title)

      id_list = []
      movie_list = movielens.titles()
      editDistances = {}
      minEditDistance = math.inf
      for i in range(len(movie_list)):
        movie = self.process_title(movie_list[i][0]).lower()

        editDistance = self.edit_distance(movie, title, max_distance)

        movie = re.sub("\s\((\d{4})\)", "", movie) # remove date
        if re.search(", the\Z", movie) != None: # switch 'the" to beginning of sentence
          movie = "the " + re.sub(", the\Z", "", movie)

        editDistance_YearRemoved = self.edit_distance(movie, title, max_distance)

        # update new minimum edit distance
        if editDistance < minEditDistance and editDistance != -1:

          minEditDistance = editDistance
        if editDistance_YearRemoved < minEditDistance and editDistance_YearRemoved != -1:

          minEditDistance = editDistance_YearRemoved

        if editDistance <= max_distance and editDistance != -1:
          if editDistance in editDistances:
            editDistances[editDistance].append(i)
          else:
            editDistances[editDistance] = [i]

        elif editDistance_YearRemoved <= max_distance and editDistance_YearRemoved != -1:
          if editDistance_YearRemoved in editDistances:
            editDistances[editDistance_YearRemoved].append(i)
          else:
            editDistances[editDistance_YearRemoved] = [i]
      
      #Find all movies that are the minimum edit distance away
      options = editDistances[minEditDistance]
      for i in options:
        id_list.append(i)

      return id_list


    def disambiguate(self, clarification, candidates):
      """Creative Feature: Given a list of movies that the user could be talking about 
      (represented as indices), and a string given by the user as clarification 
      (eg. in response to your bot saying "Which movie did you mean: Titanic (1953) 
      or Titanic (1997)?"), use the clarification to narrow down the list and return 
      a smaller list of candidates (hopefully just 1!)

      - If the clarification uniquely identifies one of the movies, this should return a 1-element
      list with the index of that movie.
      - If it's unclear which movie the user means by the clarification, it should return a list
      with the indices it could be referring to (to continue the disambiguation dialogue).

      Example:
        chatbot.disambiguate("1997", [1359, 2716]) should return [1359]
      
      :param clarification: user input intended to disambiguate between the given movies
      :param candidates: a list of movie indices
      :returns: a list of indices corresponding to the movies identified by the clarification
      """
      pass


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def binarize(self, ratings, threshold=2.5):
      """Return a binarized version of the given matrix.

      To binarize a matrix, replace all entries above the threshold with 1.
      and replace all entries at or below the threshold with a -1.

      Entries whose values are 0 represent null values and should remain at 0.

      :param x: a (num_movies x num_users) matrix of user ratings, from 0.5 to 5.0
      :param threshold: Numerical rating above which ratings are considered positive

      :returns: a binarized version of the movie-rating matrix
      """
      #############################################################################
      # TODO: Binarize the supplied ratings matrix.                               #
      #############################################################################

      # The starter code returns a new matrix shaped like ratings but full of zeros.
      binarized_ratings = np.zeros_like(ratings)
      for i in range(len(ratings)):
        for j in range(len(ratings[0])):
          r = ratings[i][j]
          if r == 0: continue
          if r > threshold: binarized_ratings[i][j] = 1
          elif r <= threshold: binarized_ratings[i][j] = -1

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return binarized_ratings


    def similarity(self, u, v):
      """Calculate the cosine similarity between two vectors.

      You may assume that the two arguments have the same shape.

      :param u: one vector, as a 1D numpy array
      :param v: another vector, as a 1D numpy array

      :returns: the cosine similarity between the two vectors
      """
      #############################################################################
      # TODO: Compute cosine similarity between the two vectors.
      #############################################################################
      lenx, leny, lenxy = 0, 0, 0
      for i in range(len(u)):
          x = v[i]
          y = u[i]
          lenx += x*x
          leny += y*y
          lenxy += x*y
      cosine_sim = lenxy / float(math.sqrt(lenx*leny))
      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return cosine_sim


    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
      """Generate a list of indices of movies to recommend using collaborative filtering.

      You should return a collection of `k` indices of movies recommendations.

      As a precondition, user_ratings and ratings_matrix are both binarized.

      Remember to exclude movies the user has already rated!

      :param user_ratings: a binarized 1D numpy array of the user's movie ratings
      :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
        `ratings_matrix[i, j]` is the rating for movie i by user j
      :param k: the number of recommendations to generate
      :param creative: whether the chatbot is in creative mode

      :returns: a list of k movie indices corresponding to movies in ratings_matrix,
        in descending order of recommendation
      """

      #######################################################################################
      # TODO: Implement a recommendation function that takes a vector user_ratings          #
      # and matrix ratings_matrix and outputs a list of movies recommended by the chatbot.  #
      #                                                                                     #
      # For starter mode, you should use item-item collaborative filtering                  #
      # with cosine similarity, no mean-centering, and no normalization of scores.          #
      #######################################################################################

      # Populate this list with k movie indices to recommend to the user.
      recommendations = []
      print(user_ratings)
      print(ratings_matrix)

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return recommendations


    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, line):
      """Return debug information as a string for the line string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      """Return a string to use as your chatbot's description for the user.

      Consider adding to this description any information about what your chatbot
      can do and how the user can interact with it.
      """
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """


if __name__ == '__main__':
  print('To run your chatbot in an interactive loop from the command line, run:')
  print('    python3 repl.py')
