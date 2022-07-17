def get_module_files(module_name):
    files = []
    for fname in tqdm(directory):
        if os.path.isfile(data_directory + os.sep + fname):
            # Full path
            if module_name in fname:
                files.append(data_directory + os.sep + fname)
    return files
