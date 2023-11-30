/*YTD - BOM - CoSo*/

/*Headline Tag - Interest Income (Phần trăm hoàn thành chỉ tiêu ngày - Lãi vay ký quỹ)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfCurrentYear DATETIME;
SET @FirstDateOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfPreviousYear DATETIME;
SET @FirstDateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),1,1,0,0,0,0));

WITH

[BadDebt] AS (
	SELECT 
		CONVERT(VARCHAR(7), [Ngay], 126) [Ngay]
		, [SoTaiKhoan]
	FROM [BadDebtAccounts]
	WHERE [Ngay] BETWEEN DATEADD(MONTH, -1, @FirstDateOfPreviousYear) AND @Date
		AND [LoaiNo] NOT IN (N'Hết nợ', N'TK đã đóng')
)

, [TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Interest Income'
)

, [PrevValuePeriod] AS (
	SELECT
		SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	WHERE [rln0019].[date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
)

, [CurrentValuePeriod] AS (
	SELECT
		SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	WHERE [rln0019].[date] BETWEEN @FirstDateOfCurrentYear AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
)

SELECT
	[CurrentValuePeriod].[InterestIncome] [InterestIncome]
	, [CurrentValuePeriod].[InterestIncome] - [PrevValuePeriod].[InterestIncome] [AbsoluteChange]
	, CASE 
		WHEN [PrevValuePeriod].[InterestIncome] = 0 THEN 0
		ELSE [CurrentValuePeriod].[InterestIncome] / [PrevValuePeriod].[InterestIncome] - 1
	END [RelativeChange]
FROM [PrevValuePeriod]
CROSS JOIN [CurrentValuePeriod]


END