# Ultimate M3U Editor

A comprehensive IPTV playlist editor and processor with GitHub Actions automation.

## Features

- **Automatic Playlist Processing**: Download and process M3U playlists from multiple sources
- **Smart Channel Grouping**: Automatically group channels by country/category
- **EPG Integration**: Add Electronic Program Guide data to channels
- **Logo Management**: Automatically assign channel logos
- **GitHub Actions**: Automated processing with daily updates
- **Multiple Export Formats**: M3U, JSON, and TXT formats
- **Channel Editor**: Easy-to-use text-based channel editing

## Quick Start

1. **Add Playlist Sources**: Edit `config/providers.txt` and add your M3U playlist URLs
2. **Configure EPG**: Edit `config/epg_sources.txt` to add EPG data sources
3. **Commit and Push**: All files to trigger automatic processing
4. **Download**: Your processed playlist from `playlists/final.m3u`

## Configuration Files

### config/providers.txt
Add your M3U playlist URLs (one per line):
```
https://example.com/playlist1.m3u
https://example.com/playlist2.m3u
```

### config/epg_sources.txt
Add EPG data sources:
```
https://example.com/epg.xml.gz
```

### config/commands.txt
Define processing pipeline:
```
IMPORT
GROUP_BY_COUNTRY
APPLY_EPG
APPLY_LOGOS
EXPORT
```

## Directory Structure

```
├── config/              # Configuration files
├── editor/              # Channel editing files
├── playlists/           # Generated playlists
├── scripts/             # Processing scripts
│   ├── modules/         # Core modules
│   ├── main.py          # Main processor
│   ├── utils.py         # Utility functions
│   └── ...             # Additional scripts
├── logs/               # Processing logs
└── .github/workflows/  # GitHub Actions
```

## Processing Pipeline

1. **Import**: Download playlists from configured sources
2. **Group**: Organize channels by country/category
3. **EPG**: Apply Electronic Program Guide data
4. **Logos**: Assign channel logos
5. **Export**: Generate final playlists

## GitHub Actions

The repository includes automated workflows:

- **Daily Processing**: Automatically updates playlists every day
- **Manual Trigger**: Run processing on-demand
- **Auto-commit**: Commits processed files back to repository

## Channel Editing

Edit channels manually in `editor/channels.txt`:

```
[Channel Name]
group: Category Name
url: http://stream.url
logo: http://logo.url
epg: channel.epg.id
```

## Output Files

- `playlists/final.m3u` - Complete processed playlist
- `playlists/channels.json` - JSON format export
- `playlists/index.html` - Web interface for playlists
- `editor/channels.txt` - Editable channel list

## Logs

Check `logs/processing.log` for detailed processing information and error messages.

## Advanced Usage

### Custom Processing Scripts

Create custom processing scripts in the `scripts/` directory and modify `scripts/main.py` to include them.

### Logo Customization

Add custom logo mappings in `scripts/logo_manager.py`.

### EPG Mapping

Customize EPG channel matching in `scripts/epg_manager.py`.

## Troubleshooting

1. **No channels found**: Check playlist URLs in `config/providers.txt`
2. **Processing errors**: Review `logs/processing.log`
3. **GitHub Actions failing**: Check repository permissions and secrets
4. **Missing logos/EPG**: Verify source URLs and internet connectivity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and feature requests, please use the GitHub Issues page.
