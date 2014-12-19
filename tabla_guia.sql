CREATE TABLE IF NOT EXISTS `ingreso_guia` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`num_guia` int(6) NOT NULL,
	`fecha` date NOT NULL,
	`boleto` varchar(5) NOT NULL,
	`marca` varchar(5) NOT NULL,
	`rup` varchar(12) NOT NULL,
	PRIMARY KEY (`id`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=0 ;
