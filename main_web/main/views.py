
from django.shortcuts import render, redirect, get_object_or_404
from .models import Portfolio
from .forms import PortfolioForm
import json
import os

import subprocess

def portfolio_select(request):
	portfolios = Portfolio.objects.all()
	if request.method == 'POST':
		if 'portfolio_id' in request.POST:
			portfolio_id = request.POST['portfolio_id']
			portfolio = Portfolio.objects.get(id=portfolio_id)
			_run_fetch_and_main(portfolio)
			return redirect('article_list', portfolio_id=portfolio_id)
		form = PortfolioForm(request.POST)
		if form.is_valid():
			portfolio = form.save()
			_run_fetch_and_main(portfolio)
			return redirect('article_list', portfolio_id=portfolio.id)
	else:
		form = PortfolioForm()
	return render(request, 'main/portfolio_select.html', {'form': form, 'portfolios': portfolios})

# Helper to run backend scripts
def _run_fetch_and_main(portfolio):
	import sys
	import re
	backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend'))
	fetch_script = os.path.join(backend_dir, 'fetch_data.py')
	main_script = os.path.join(backend_dir, 'main.py')
	# Clean up assets: remove special chars, split by comma, strip whitespace
	raw_assets = portfolio.assets.replace(';', ',')
	keywords = [re.sub(r'[^\w\s-]', '', k).strip() for k in raw_assets.split(',') if k.strip()]
	assets_arg = ','.join(keywords)
	subprocess.run([sys.executable, fetch_script, assets_arg], cwd=backend_dir, check=True)
	subprocess.run([sys.executable, main_script], cwd=backend_dir, check=True)

def article_list(request, portfolio_id):
	portfolio = get_object_or_404(Portfolio, id=portfolio_id)
	# Always read from backend directory
	backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend'))
	relevant_path = os.path.join(backend_dir, 'relevant_articles.json')
	content_path = os.path.join(backend_dir, 'content.json')
	try:
		with open(relevant_path) as f:
			relevancies = json.load(f)
		with open(content_path) as f:
			articles = json.load(f)
		# Pair articles and relevancies
		article_objs = []
		for art, rel in zip(articles, relevancies):
			rel_data = json.loads(rel) if isinstance(rel, str) else rel
			article_objs.append({
				'title': art[0],
				'content': art[1],
				'url': art[2],
				'is_relevant': rel_data.get('is_relevant', ''),
				'reason': rel_data.get('reason', '')
			})
		# Filter out 'not relevant' articles
		article_objs = [a for a in article_objs if a['is_relevant'] != 'not relevant']
		# Sort by relevancy
		relevancy_order = {'highly relevant': 0, 'relevant': 1, 'somewhat relevant': 2}
		article_objs.sort(key=lambda x: relevancy_order.get(x['is_relevant'], 3))
	except Exception as e:
		article_objs = []
	return render(request, 'main/article_list.html', {'portfolio': portfolio, 'articles': article_objs})
