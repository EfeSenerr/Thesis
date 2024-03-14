# Results Folder

This folder includes the results of the topic modeling and the analysis of the tweets. All the results are discussed in the thesis in detail. The results are presented in the form of tables, graphs, and other visualizations.

This folder also includes the two base BERTopic models that are discussed in the thesis, which can be found in the subfolders. They are both trained on a 1% random sample of the tweets. The remaining data is transformed according to the base model’s topic allocations.

Explanation for individual files:

- **first_approach_base_model.csv**: This file presents the topic representations of the base model from the first approach. It lists over 7000 topics and their respective representative words.
- **first_approach_monthly_distribution.csv**: This file presents the monthly distribution of the topic modeling results from the first approach after the transformation of the remaining data.
- **first_approach_top_50_topics_hierarchical_interactive.html**: This file presents the top 50 topics from the first approach in an interactive hierarchical visualization.
- **first_approach_top_50_topics_interactive.html**: This file presents the top 50 topics from the first approach in an interactive visualization. The topics are normalized monthly and with respect to the top 50 topics.
- **first_approach_top_50_topics.csv**: This file presents the top 50 topics from the first approach, including the presentative tweets, words, counts, and OpenAI labels.
- **first_approach_top_250_topics_intertopic_distance_interactive.html**: This file presents the intertopic distance map of the top 250 topics from the first approach in an interactive visualization.

- **second_approach_base_model.csv**: This file presents the topic representations of the base model from the second approach. It lists over 1000 topics and their respective representative words.
- **second_approach_monthly_distribution.csv**: This file presents the monthly distribution of the topic modeling results from the second approach after the transformation of the remaining data.
- **second_approach_top_50_topics_frequency_interactive.html**: This file presents the top 50 topics from the second approach in an interactive visualization. However, the topics are not normalized, highlighting the difficulty in analyzing the trends in a frequency visualization.
- **second_approach_top_50_topics_interactive.html**: This file presents the top 50 topics from the second approach in an interactive visualization. The topics are normalized monthly and with respect to the top 50 topics.
- **second_approach_top_50_topics.csv**: This file presents the top 50 topics from the second approach, including the presentative tweets, words, counts, and OpenAI labels.

- **total_collected_tweets_interactive.html**: This file presents the total number of tweets in the dataset, the deleted tweets, and the collected tweets in an interactive visualization.#
