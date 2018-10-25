import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import random
import os
import json

FIGURE_DIR = '../clustering/plot_figures'

def create_cluster_json(cluster_dict):
    cluster_json = {}
    for key in cluster_dict:
        cluster_json[str(key)] = cluster_dict[key]
    return cluster_json

def empty_figure_folder(folder=FIGURE_DIR):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def load_data(file_name):
    df = pd.read_csv(file_name)
    return df


def geo_clustering(df):
    lat, lng = df['latitude'], df['longitude']
    kmeans = KMeans(n_clusters=6)
    kmeans.fit(list(zip(lat, lng)))
    centers = np.array(kmeans.cluster_centers_)
    labels = kmeans.labels_
    plt.scatter(lat, lng, c=labels)
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1])
    return centers, labels


def center_based_list(centers, labels, df):
    lat, lng, keywords = df['latitude'], df['longitude'], df['keyword']
    dick = {}
    for idx, cen in enumerate(labels):
        location = {}
        location['lat'] = lat[idx]
        location['log'] = lng[idx]
        location['keywords'] = keywords[idx]
        if cen in dick:
            dick[cen].append(location)
        else:
            dick[cen] = []
            dick[cen].append(location)

    location_stats = {}
    keyword_stats = {}
    for label in dick:
        cluster_list = dick[label]
        cluster_stats = {}
        for item in cluster_list:
            words = item['keywords'].split(',')
            for word in words:
                if word not in ["Food", "Water", "Medicines", "Clothing", "Appliances", "Others"]: word = "Others"
                if word not in cluster_stats:
                    cluster_stats[word] = 1
                else:
                    cluster_stats[word] += 1

                if word not in keyword_stats:
                    keyword_stats[word] = 1
                else:
                    keyword_stats[word] += 1

            location_stats[label] = cluster_stats

    return dick, location_stats, keyword_stats


def plot_top_location_stats(centers, location_stats, top_n=6):
    base_colors = "grcmyb"
    plot_data_json = []

    # _ is cluster centers
    for _ in location_stats:
        individual_cluster_json = {}
        sizes = []
        clustered_location_stats = location_stats[_]
        for key in clustered_location_stats:
            sizes.append(clustered_location_stats[key])
        sizes.sort(reverse=True)
        sizes = sizes[:top_n]

        lat, lng = centers[_]
        figure_name = "{}_{}.png".format(lat, lng)
        figure_path = os.path.join(FIGURE_DIR, figure_name)
        fig = figure()
        explode_split = random.randint(1, top_n)
        explode = (0.1,) * explode_split + (0.0,) * (top_n - explode_split)
        colors = ''.join(random.sample(base_colors, len(base_colors)))
        plt.pie(sizes, explode=explode, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=100)
        plt.axis('equal')
        fig.savefig(figure_path)

        individual_cluster_json['figure_path'] = figure_path
        individual_cluster_json['data'] = clustered_location_stats
        individual_cluster_json['latitude'] = lat
        individual_cluster_json['longitude'] = lng

        plot_data_json.append(individual_cluster_json)

    return plot_data_json


def plot(file_name='large_set.csv'):
    empty_figure_folder()
    df = load_data(file_name)
    centers, labels = geo_clustering(df)
    dick, location_stats, keyword_stats = center_based_list(centers, labels, df)
    all_points_json = create_cluster_json(dick)
    clustering_data = plot_top_location_stats(centers, location_stats)
    with open('data.json', 'w') as fp:
        json.dump(clustering_data, fp)
    with open('all_points.json', 'w') as fp:
        json.dump(all_points_json, fp)

plot()
