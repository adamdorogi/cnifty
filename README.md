# cnifty

## Generator

TODO:

- nft id, nft ticker, nft name, project name, collection name, copyright, twitter, website, etc. to output metadata
- change to OOP?
- allow option to provide premade images (provide separate traits file in the format of metadata.csv)
- allow option to specify variants of attributes to match with specific attributes (e.g. brown man bun to match brown hairs only)
- pydoc comments
- sanity check to make sure images are all same size?
- sanity check to make sure combinations exceeds amount? generate statistic on how likely it's going to take based on combination possibilites and amount?
- lazily load images in `__generate_images` function
- reverse stats, i.e. list of ids for certain trait

# (exclude ipfs from metadata, have separate command to add to ipfs and return ipfs hashes)

# (minting command should take both ipfs hashes and image metadata)
