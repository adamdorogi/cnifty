import datetime
import click
import csv
import pathlib
import numpy as np
from functools import reduce
from PIL import Image, UnidentifiedImageError


@click.command()
@click.argument('token-name')
@click.argument('in-file', type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=pathlib.Path))
@click.argument('out-dir', type=click.Path(file_okay=False, writable=True, resolve_path=True, path_type=pathlib.Path))
@click.argument('amount', type=click.IntRange(min=1))
@click.option('--seed', '-s', type=click.IntRange(min=0), help='A seed to initialize the random generator.')
def generate_content(token_name, in_file, out_dir, amount, seed):
    """
    Generate NFT images, metadata and rarity statistics.

    Generate a set of AMOUNT images, associated metadata and rarity statistics
    to OUT_DIR from the traits specified in IN_FILE.

    IN_FILE should be a CSV file containing trait types, names, rarity weights
    and image paths.

    The trait type defines the category of the trait, the trait name defines the
    name of the trait, the trait rarity weights define the approximate
    distribution of the traits withing their trait type, and the image path
    defines the relative image path of the trait image file.

    The order of the traits in the CSV file are preserved when constructing the
    images.

    Example:

    \b
    Type,Name,Rarity Weight,Image Path
    Background,Green Background,4,./Background/Green Background.png
    Mouth,Smiling Mouth,3,./Mouth/Smiling Mouth.png
    Hair,Blonde Hair,6,./Hair/Blonde Hair.png
    Accessories,,4,
    Mouth,Tongue Out,4,./Mouth/Tongue Out.png
    ...
    """
    rng = np.random.default_rng(seed=seed)
    traits = __load_traits(file_path=in_file)
    rarity_weight_groups = __get_normalized_rarity_weight_groups(traits=traits)
    token_data = __generate_token_data(
        traits, rarity_weight_groups, amount, rng)
    out_dir = out_dir.joinpath(pathlib.Path(
        f'{token_name} {datetime.datetime.now()}'))
    out_dir.mkdir(parents=True)

    __generate_metadata(token_name=token_name,
                       token_data=token_data, out_dir=out_dir)
    __generate_statistics(token_name=token_name,
                         token_data=token_data, out_dir=out_dir)
    __generate_images(token_name=token_name,
                     token_data=token_data, out_dir=out_dir)


def __load_traits(file_path):
    """
    """
    # Load the traits CSV file
    with open(file_path) as csvfile:
        try:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            traits = np.array([(type or None, name or None, int(rarity_weight) or 0, image_path or None)
                              for type, name, rarity_weight, image_path in reader], dtype=object)
        except ValueError:
            raise click.ClickException(f'Invalid CSV file: {file_path}')

    # Get the image paths and their indexes
    image_paths_index = (traits[:, 3] != None, 3)
    image_paths = traits[image_paths_index]

    # Load and replace the image paths with their respective images
    with click.progressbar(length=image_paths.size, label='Loading trait images', show_percent=True, show_pos=True, item_show_func=lambda a: a) as bar:
        traits[image_paths_index] = [_load_trait_image(
            image_path=file_path.parent.joinpath(pathlib.Path(image_path)).resolve(), progress_bar=bar) for image_path in image_paths]

    return traits


def _load_trait_image(image_path, format='PNG', mode='RGBA', progress_bar=None):
    """
    """
    # Update the progress bar, if it exists
    if progress_bar:
        progress_bar.update(n_steps=1, current_item=str(image_path))

    # Open the image at the image path
    try:
        return Image.open(fp=image_path, formats=[format]).convert(mode=mode)
    except FileNotFoundError:
        raise click.ClickException(f'File not found: {image_path}')
    except UnidentifiedImageError:
        raise click.ClickException(f'Invalid image file: {image_path}')


def __get_normalized_rarity_weight_groups(traits):
    """
    """
    # Group rarity weights by trait type
    sorted_indexes = traits[:, 0].argsort()
    sorted_traits = traits[sorted_indexes]

    split_indexes = np.unique(ar=sorted_traits[:, 0], return_index=True)[1][1:]

    rarity_weights = sorted_traits[:, 2].astype(dtype=np.float64)
    indexed_rarity_weights = np.column_stack(
        tup=(sorted_indexes, rarity_weights))

    indexed_rarity_weight_groups = np.split(
        ary=indexed_rarity_weights, indices_or_sections=split_indexes)

    # Normalize each group of rarity weights
    normalized_indexed_rarity_weight_groups = [_normalize_indexed_rarity_weights(
        indexed_rarity_weight_group) for indexed_rarity_weight_group in indexed_rarity_weight_groups]
    return normalized_indexed_rarity_weight_groups


def _normalize_indexed_rarity_weights(weight_matrix):
    """
    """
    weights = weight_matrix[:, 1]
    weight_matrix[:, 1] = weights/weights.sum()
    return weight_matrix


def __generate_token_data(traits, rarity_weight_groups, amount, rng):
    """
    """
    # Initialise an empty set to keep track of used traits
    generated_traits = set()
    # Initialise the array of picked traits for each token
    token_data = np.empty(
        shape=(amount, len(rarity_weight_groups), 4), dtype=object)

    # Keep generating random traits until we have the desired amount
    with click.progressbar(length=amount, label='Generating token data') as bar:
        while bar.pos < amount:
            random_traits = __get_random_traits(
                traits=traits, rarity_weight_groups=rarity_weight_groups, rng=rng)
            random_trait_names = tuple(random_traits[:, 1])
            # Keep the random traits if they haven't been generated before
            if random_trait_names not in generated_traits:
                generated_traits.add(random_trait_names)
                token_data[bar.pos] = random_traits

                bar.update(1)

    # Remove the rarity weights as they are no longer needed
    return np.delete(arr=token_data, obj=2, axis=2)


def __get_random_traits(traits, rarity_weight_groups, rng):
    """
    """
    random_trait_indexes = np.sort(a=[rng.choice(a=rarity_weight_group[:, 0], p=rarity_weight_group[:, 1])
                                      for rarity_weight_group in rarity_weight_groups]).astype(dtype=np.int64)
    return traits[random_trait_indexes]


def __generate_metadata(token_name, token_data, out_dir):
    """
    """
    # Map the trait type-name pairs into dictionaries
    metadata = [{
        'Name': f'{token_name} #{trait[0]+1}', **dict(trait[1])} for trait in enumerate(token_data[:, :, :2])]

    with open(out_dir.joinpath(pathlib.Path('metadata.csv')), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(metadata[0]))
        writer.writeheader()
        writer.writerows(metadata)


def __generate_statistics(token_name, token_data, out_dir):
    """
    """
    out_dir = out_dir.joinpath(pathlib.Path('statistics'))
    out_dir.mkdir()

    trait_frequencies = __generate_trait_frequencies(
        token_data=token_data, out_dir=out_dir)
    trait_count_frequencies = __generate_trait_count_frequencies(
        token_data=token_data, out_dir=out_dir)
    _ = __generate_rarities(token_name=token_name, trait_frequencies=trait_frequencies,
                           trait_count_frequencies=trait_count_frequencies, out_dir=out_dir)


def __generate_trait_frequencies(token_data, out_dir):
    """
    """
    # Filter token data from None values
    filtered_traits = np.vstack(token_data[:, :, :2])

    # Get unique trait type-name pairs and their frequencies
    unique_traits, unique_traits_inverse, unique_trait_frequencies = np.unique(
        filtered_traits.astype(dtype='U'), return_inverse=True, return_counts=True, axis=0)
    trait_statistics = np.column_stack(
        (unique_traits.astype(dtype=object), unique_trait_frequencies))

    with open(out_dir.joinpath(pathlib.Path('trait_frequencies.csv')), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Name', 'Frequency'])
        writer.writerows(trait_statistics)

    # Return trait frequencies of each token
    trait_frequencies = np.split(
        unique_trait_frequencies[unique_traits_inverse], len(token_data))
    return np.array(trait_frequencies)


def __generate_trait_count_frequencies(token_data, out_dir):
    """
    """
    # Count not None traits for each token
    traits_counts = np.count_nonzero(token_data[:, :, 1], axis=1)

    # Get unique counts and their frequencies
    unique_trait_counts, unique_trait_counts_inverse, unique_trait_count_frequencies = np.unique(
        traits_counts, return_inverse=True, return_counts=True)
    trait_count_statistics = np.column_stack(
        (unique_trait_counts, unique_trait_count_frequencies))

    with open(out_dir.joinpath(pathlib.Path('trait_count_frequencies.csv')), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Count', 'Frequency'])
        writer.writerows(trait_count_statistics)

    # Return trait count frequencies of each token
    trait_count_frequencies = unique_trait_count_frequencies[unique_trait_counts_inverse]
    return trait_count_frequencies


def __generate_rarities(token_name, trait_frequencies, trait_count_frequencies, out_dir):
    """
    """
    # Combine trait frequencies and trait count frequencies
    frequencies = np.column_stack((trait_frequencies, trait_count_frequencies))

    # Calculate rarity scores
    rarity_scores = np.fromiter((np.sum(
        len(frequencies)/x) for x in frequencies), dtype=np.float64)
    token_names = np.array(
        [f'{token_name} #{i+1}' for i in range(len(frequencies))])
    rarity_score_statistics = np.column_stack((token_names, rarity_scores))

    with open(out_dir.joinpath(pathlib.Path('rarity_scores.csv')), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Rarity Score'])
        writer.writerows(rarity_score_statistics)

    # Return rarity scores of each token
    return rarity_scores


def __generate_images(token_name, token_data, out_dir):
    """
    """
    token_data_images = token_data[:, :, 2]
    with click.progressbar(iterable=token_data_images, label='Saving images') as bar:
        for trait_images in bar:
            combined_image = reduce(__combine_images, trait_images)
            combined_image.save(out_dir.joinpath(
                pathlib.Path(f'{token_name} #{bar.pos+1}.png')))


def __combine_images(first, second):
    """
    """
    if first and second:
        # TODO: `.copy()`? or `.copy()` at `initial=`?
        return Image.alpha_composite(im1=first, im2=second)
    elif first:
        return first
    elif second:
        return second
