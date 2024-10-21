import neat
import pickle

def create_genome_from_text(config_path):
    # Load the NEAT configuration
    config = neat.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        config_path
    )
    
    # Create a new genome object with the key 3669
    genome = neat.DefaultGenome(3669)

    # Configure the genome based on the config
    genome.configure_new(config.genome_config)

    # Assign biases to the nodes (only if they exist in the genome)
    node_biases = {
        0: -2.043385792870298,
        13: -0.34531379376166815,
        356: 2.4569855686792152,
        383: -0.18820088252204575,
        486: -1.164868949123984,
        531: 1.1241829902499156,
        684: 1.0405222644454344,
        714: 2.284936483508302,
    }

    for key, bias in node_biases.items():
        if key in genome.nodes:
            genome.nodes[key].bias = bias

    # Define connections with weights and enabled status
    connections_data = [
        ((-3, 0), -2.304647222193718, True),
        ((-3, 13), -0.34817974317817335, False),
        ((-2, 0), 1.486773936947755, True),
        ((-2, 356), -0.8380634013876055, True),
        ((-1, 356), -0.4349566462162243, True),
        ((383, 486), 2.2183836510092823, True),
        ((531, 356), 1.7213462959633223, False),
        ((531, 714), 0.44396347131278996, True),
        ((684, 356), 0.6795804225266872, True),
        ((714, 356), 1.5034061955350722, True),
    ]

    # Add connections to the genome
    for key, weight, enabled in connections_data:
        if key not in genome.connections:
            genome.connections[key] = config.genome_config.connection_gene_type(key)
        genome.connections[key].weight = weight
        genome.connections[key].enabled = enabled

    # Save the genome as a pickle file
    with open("best_genome.pickle", "wb") as f:
        pickle.dump(genome, f)

# Call the function with the path to the NEAT config file
create_genome_from_text("neat-config.txt")
