from lncdtask.rundialog import RunDialog

def test_next_run():
    rd = RunDialog()
    assert rd.info['run_num'] == 1
    rd.next_run()
    assert rd.info['run_num'] == 2


def test_has_change():
    rd = RunDialog() # subjid probably "000"
    rd.info['subjid'] = 'a new subject id'
    assert rd.has_changed('subjid')
