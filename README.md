### Create and Activate Virtual Environment
```bash
python3 -m venv leetcode_venv
```

```bash
source venv/bin/activate
```

### Alfa LeetCode API Setup

Please follow the official instructions from the [Alfa LeetCode API repository](https://github.com/alfaarghya/alfa-leetcode-api) to set up the project

Fork the repository on GitHub, then clone your fork:

```bash
git clone https://github.com/<your-username>/alfa-leetcode-api.git
```

```bash
cd alfa-leetcode-api
```

```bash
npm install
```

## CrewAI Setup

Please follow the official instructions from CrewAI (https://docs.crewai.com/en/installation) to set up the project

install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
uv tool install crewai
```

## Install other requirements
```bash
pip install dotenv neo4j pyyaml streamlit
```


# Running the App


open another terminal and run:
```bash
streamlit run app.py
```