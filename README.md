# From Hashtags to Ballot Boxes: A Close Look at the 2023 Turkish Elections

## Repository Folder Structure

    .
    ├── analysis               # Files related to topic modeling and analysis
    ├── collection             # Files related to the collection of tweets 
    ├── results                # Topic modeling results
    │   ├── first_approach_base_model
    │   └── second_approach_base_model
    └── src                    # Source files
        └── figures            # Visualizations used in the thesis

This repository contains the source code and sample data used in the thesis "From Hashtags to Ballot Boxes: A Close Look at the 2023 Turkish Elections". The repository is organized into four main folders: `analysis`, `collection`, `results`, and `src`.

Every subfolder includes its own README file that explains the contents of the subfolder in detail.

The thesis latex repository can be found [under this link](https://github.com/EfeSenerr/Thesis_paper), where two-sided versions of the thesis can be found.

## Abstract

This thesis dives into the depths of Turkish Twitter political discourse around the May 2023 general elections, collecting and analyzing around 150 million tweets from July 2022 to June 2023. BERTopic is leveraged as the neural topic model to uncover the trending themes. A base model is trained on a 1% random sample, with the remaining data transformed according to the base model’s topic allocations.

To discover the key themes of the political discourse on Twitter, over 1000 topic clusters are revealed initially. The trending topics, their representative words, and counts are presented through tables, graphs, and other visualizations. The thesis discovers that topics associated with the government engage with nationalism, criticism and praise of political figures, demands and wishes from the government, and President Erdogan’s reelection chance. On the other hand, opposition-related topics focus on presidential candidacy, coalition dynamics, biased judiciary, the economic situation, and disinformation against the opposition block.

This thesis provides insights into the correlation between real-life events and trending topics on Twitter, where the political discourse on Twitter and the coalition strategies,
public speeches, and announcements are also compared and discussed. Furthermore, the thesis performs a comparative analysis by contrasting the results with other research
analyzing different elections and political domains.

In conclusion, this thesis contributes to the academic environment by pioneering one of the first topic modeling analyses on Turkish political discourse utilizing big data,
which sheds light on the May 2023 general elections and aims to better understand Turkish political discourse and motivate future research by presenting the methodologies
and findings.
