google.load('visualization', '1', {'packages': ['corechart']});
		google.setOnLoadCallback(drawPies);

		function drawPies() {
			var Hpie = new google.visualization.Query('https://docs.google.com/spreadsheet/tq?range=A6%3AB9&key=0Ao3iZjz2mPXEdG5YT2FMc0owSDRuLUtpYmRwaktMeHc&gid=0&headers=0');
			var Spie = new google.visualization.Query('https://docs.google.com/spreadsheet/tq?range=A1%3AB4&key=0Ao3iZjz2mPXEdG5YT2FMc0owSDRuLUtpYmRwaktMeHc&gid=0&headers=0');
			Hpie.send(handleHpieResponse);
			Spie.send(handleSpieResponse);
		};
		
		function handleHpieResponse(response) {
			if (response.isError()) {
				alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
				return;
			}

			var Htotals = response.getDataTable();         
			var options = {//title: 'House',
							// titleTextStyle:{fontSize:'1'},
							legend:{position:'none'},
							chartArea:{height: '80%',width:'90%'},
							colors:['white','blue','red'],
							backgroundColor: 'FFFFFF',
							is3D: 'true'
						};
			var chartHP = new google.visualization.PieChart(document.getElementById('mn_house_pie_div'));
			chartHP.draw(Htotals, options);
		};
		function handleSpieResponse(response) {
			if (response.isError()) {
				alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
				return;
			}

			var Stotals = response.getDataTable();         
			var options = {//title: 'Senate',
							// titleTextStyle:{fontSize:'14'},
							legend:{position:'none'},								
							chartArea:{height: '80%',width:'90%'},
							colors:['grey','blue','red'],
							backgroundColor: 'FFFFFF',
							is3D: 'true'
						};
			var chartSP = new google.visualization.PieChart(document.getElementById('mn_sen_pie_div'));
			chartSP.draw(Stotals, options);
		};